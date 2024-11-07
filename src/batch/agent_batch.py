# Process each record in the event
import base64
import json
import os
import tempfile
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from pdf2image import convert_from_bytes, pdfinfo_from_path

from constants import BUCKET_NAME_RAW_IMAGES, BUCKET_RAW_PDFS, REGION_AWS, \
    MODEL_LLM, SQS_DLQ_METADATA_PDF_URL
from dynamo import dynamo_put_status_finished
from s3 import check_image_exists, upload_image_to_s3
from utils.send_to_dlq import send_to_dlq
from utils.uri_decode import uri_decode

load_dotenv()


@dataclass
class Metadata:
    folder_id: Optional[str]
    title: Optional[str]
    capture_time: Optional[str]
    author: Optional[str]


# TODO: remove Print statements when dev'ing is complete
def process_event():
    # Future TODO: create CloudWatch insights dashboard using log group and log stream
    # print(f"Log Group: {context.log_group_name}")
    # print(f"Log Stream: {context.log_stream_name}")
    # Get the MESSAGE_BODY environment variable
    message_record = os.getenv('SQS_MESSAGE')
    print(f"Test Override message{os.getenv("TEST_OVERRIDE")}")
    print(f"Received SQS Message: {message_record}")

    # Parse the JSON message
    message = json.loads(message_record)
    print(f"SQS Message: {message}")
    for record in message["Records"]:
        try:
            # Get the SQS message body
            message_body = json.loads(record["body"])
            print("record:::", record["receiptHandle"])
            if not message_body:
                print("message_body:::", message_body)
                send_to_dlq(SQS_DLQ_METADATA_PDF_URL, message_body)
                raise Exception("No message_body for SQS Message Record:::")
            print("metadata:::", message_body)
            # Create an instance of Metadata dataclass
            folder_metadata_pdf = Metadata(
                folder_id=str(message_body.get('folder_id')),
                title=message_body.get('title', None),
                capture_time=message_body.get('capture_time', None),
                page_length=str(message_body.get('page_length', None)),
                author=message_body.get('author', None)
            )
            # Delete the message from the SQS queue so it is not repressed
            # sqs_message_delete(record["receiptHandle"])
            process_image(folder_metadata_pdf)
            # TODO: Remove send_to_dlq once Testing if DLQ working
            # send_to_dlq(SQS_DLQ_METADATA_PDF_URL, message_body)
        except ClientError as e:
            raise Exception(f"Failed to add item: {e.response['Error']['Message']}, message sent to DLQ_BATCH")
        except Exception as e:
            raise Exception("An error occurred in process_opensearch_document:::", str(e))


def process_image(metadata) -> str:
    # Initialize boto3 clients
    client_s3 = boto3.client('s3')
    try:
        print("metadata['guid']:::", metadata.guid)

        # Get the PDF from S3
        s3_response = client_s3.get_object(Bucket=BUCKET_RAW_PDFS, Key=metadata.guid)
        pdf_bytes_read = s3_response['Body'].read()  # Read the PDF content (bytes)

        # Use a temporary file to store the PDF content
        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes_read)
            temp_pdf.flush()  # Ensure data is written to disk

            # Now use pdfinfo_from_path with the temporary file's path
            info = pdfinfo_from_path(temp_pdf.name)
            total_pages = info['Pages']
            print("Total Pages in PDF::", total_pages)

            # Convert PDF to images (one image per page)
            for page in range(1, total_pages + 1):
                print(f"Processing page: {page}")
                # Create a unique image ID
                bucket_key_image = f"{metadata.folder_id}/{page}"
                # Check if image exists in S3 already
                if check_image_exists(BUCKET_NAME_RAW_IMAGES, bucket_key_image):
                    return f"PDF page has already processed and exists in S3 bucket_key: {bucket_key_image}"

                # Convert the specified page of the PDF to an image
                images = convert_from_bytes(pdf_bytes_read, dpi=300, first_page=page, last_page=page)
                for image in images:
                    # Using a context manager to handle BytesIO properly
                    with BytesIO() as img_byte_arr:
                        # Save the image as PNG to the byte stream
                        image.save(img_byte_arr, format='PNG')
                        img_byte_arr.seek(0)  # Reset the stream's position to the start

                        # Upload the image to S3
                        # TODO: If image stored in OpenSearch works well, then ask PV wants to also store in s3
                        #  (this would be duplicate storage), otherwise remove these lines and destroy s3 bucket
                        upload_image_to_s3(bucket_name=BUCKET_NAME_RAW_IMAGES,
                                           bucket_key=bucket_key_image,
                                           image=img_byte_arr)

                    # Check if the image exists in S3 before further processing
                    if check_image_exists(BUCKET_NAME_RAW_IMAGES, bucket_key_image):
                        # Compress the image using another BytesIO object
                        compressed_image_io = BytesIO()
                        image.save(compressed_image_io, format='PNG', quality=30)  # Adjust quality as needed
                        compressed_image_io.seek(0)  # Reset the stream's position to the start

                        # Get the compressed image bytes
                        compressed_image_bytes = compressed_image_io.read()
                        print(f"Compressed image size: {len(compressed_image_bytes)} bytes")

                        # TODO: Remove done testing complete - Optionally, save the compressed image to a file to check its size
                        # with open("compressed_image.jpg", "wb") as f:
                        #     f.write(compressed_image_bytes)

                        # Process OpenSearch document with the compressed image
                        process_opensearch_document(metadata, bucket_key_image, compressed_image_bytes, page=page)
                        print(f"PDF page processed and uploaded to S3 bucket_key: {bucket_key_image}")
    except Exception as e:
        # Catch and print the exception with a custom message
        raise Exception(f"An error occurred in process_image: {str(e)}")


def process_opensearch_document(metadata, bucket_key_image, image_binary, page: int) -> None:
    # Get s3 client
    # client_s3 = boto3.client('s3')
    # try:
    #     # Download the object from S3
    #     file_bytes = client_s3.get_object(Bucket=BUCKET_NAME_RAW_IMAGES, Key=bucket_key_image)
    #     # Read the file's content (bytes)
    #     file_bytes_read = file_bytes['Body'].read()
    #     print("file_bytes_read:::")
    # except Exception as e:
    #     raise Exception("An error occurred in get_s3_object:::", str(e))
    encoded_image = base64.b64encode(image_binary).decode()
    # print(len(encoded_image))
    # print(encoded_image[0:250])
    # Future TODO: should we ignore comments on social media posts?
    dict = {
        "summary": "",
        "logo": {},
        "weapon": {},
        "physical_features": {},
        "physical_activity": {},
        "false_advertising": {},
        "patent": {},
        "intellectual_property": {},
        "trademark": {},
        "copyright": {},
        "trade_secret": {},
        "infringement": {},
        "product": {},
        "sales": {},
        "liability": {},
        "criminal": {},
        "defamation": {},
        "slander": {},
        "text": {},
        "other": {},
    }
    dict_string = json.dumps(dict)
    prompt = f"""
    ### MetaData ###
    {metadata}
    ### Dictionary ###
    {dict_string}
    ### Task ##
        You are an Image Analyst at a legal firm.

        Analyze the provided image and its associated text to generate a detailed summary.
        Extract key insights and observations, and populate the dictionary: {dict_string} with 
        descriptive keys and values based on the content of the image and text. 
        Include additional key-value pairs as necessary, ensuring all relevant 
        information is accurately captured.

        If a particular key does not apply to the image or text, leave its value empty. 

        Your response should only be in a valid JSON string object.
    """

    # Get bedrock client
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION_AWS)

    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": encoded_image
                        },
                    }
                ],
            }
        ],
    }
    # Dont send the json.dumps(native_request) to the model directly -- it will fail sometimes
    request_body = json.dumps(native_request)
    print("HERE::")
    try:
        # Invoke the model with the request
        response_summary = bedrock_runtime.invoke_model(modelId=MODEL_LLM,
                                                        body=request_body,
                                                        accept="application/json",
                                                        contentType="application/json")
        resp = json.loads(response_summary['body'].read().decode("utf-8"))
        response_sum = json.loads(resp['content'][0]['text'])

        print("response_summary:::", response_sum)
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{MODEL_LLM}'. Reason: {e}")
        raise Exception(f"An error occurred in invoke_model {MODEL_LLM}:::", str(e))

    try:
        # TODO: configure opensearch before this can run
        # Check the status of the OpenSearch Index to make sure it's Active and can receive Inserts
        # if not check_index_exists(OPENSEARCH_DOMAIN_NAME):
        #     raise Exception("Opensearch Index does not exist:::")
        page_summary = {
            "summary": response_sum.get('summary', None),
            "logo": response_sum.get('logo', None),
            "false_advertising": response_sum.get('false_advertising', None),
            "patent": response_sum.get('patent', None),
            "intellectual_property": response_sum.get('intellectual_property', None),
            "trademark": response_sum.get('trademark', None),
            "copyright": response_sum.get('copyright', None),
            "trade_secret": response_sum.get('trade_secret', None),
            "infringement": response_sum.get('infringement', None),
            "product": response_sum.get('product', None),
            "sales": response_sum.get('sales', None),
            "liability": response_sum.get('liability', None),
            "criminal": response_sum.get('criminal', None),
            "defamation": response_sum.get('defamation', None),
            "slander": response_sum.get('slander', None),
            "text": response_sum.get('text', None),
            "other": response_sum.get('other', None),
        }

        capture_summary = {
            "folder_id": metadata.folder_id,
            "title": metadata.title,
            "capture_time": metadata.capture_time,
            "page_length": metadata.page_length,
            "author": metadata.author
        }
        document = {
            "id": f"{metadata.guid}_{page}",
            "page_name": f"{metadata.name}_{page}",
            "image_binary": image_binary,
            "location": {
                "bucket_name_pdf": BUCKET_RAW_PDFS,
                "bucket_key_pdf": metadata.guid,
                "bucket_name_raw_image": BUCKET_NAME_RAW_IMAGES,
                "bucket_key_raw_image": bucket_key_image,
            },
            "capture_summary_json": json.dumps(capture_summary),
            "capture_summary": capture_summary,
            "page_summary_json": json.dumps(page_summary),
            "page_summary": page_summary
        }
        # submit_to_os(document)
        # # Cleanup: Manually delete the temporary file
        # os.remove(encoded_image)
        dynamo_put_status_finished(metadata.guid, "completed")
    except Exception as e:
        dynamo_put_status_finished(metadata.guid, "failed")
        raise Exception("An error occurred in process_opensearch_document:::", str(e))


# Run the function
process_event()
