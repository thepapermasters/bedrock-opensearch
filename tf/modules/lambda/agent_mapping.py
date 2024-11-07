import datetime
import json
import os
import urllib.error
import urllib.parse
import urllib.request

import boto3

# Constants - Dynamo
DYNAMO_TABLE_TRACKER = os.getenv("DYNAMO_TABLE_TRACKER")
print("DYNAMO_TABLE_TRACKER::", DYNAMO_TABLE_TRACKER)
SQS_QUEUE_METADATA_PDF_URL = os.getenv("SQS_QUEUE_METADATA_PDF_URL")
print("SQS_QUEUE_METADATA_PDF_URL::", SQS_QUEUE_METADATA_PDF_URL)
REGION_AWS = os.getenv('REGION_AWS')
PARTITION_KEY_BUCKET_KEY = "BUCKET_KEY"
ATTRIBUTE_FOLDER_ID = "FOLDER_ID"
ATTRIBUTE_CREATED_AT = "CREATED_AT"
ATTRIBUTE_STATUS = "STATUS"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_COMPLETED = "COMPLETED"
STATUS_ERROR = "ERROR"


def get_token() -> str:
    # login credentials
    api_login_name = os.getenv('API_AI_AGENT_NAME_MAPPING_USER')
    api_password = os.getenv('API_AI_AGENT_NAME_MAPPING_PASSWORD')
    # URL for the API authentication
    url = f"{os.getenv('API_AI_AGENT_NAME_MAPPING_URL')}/auth"
    # Payload for the POST request
    payload = {
        'login_name': api_login_name,
        'password': api_password
    }
    # Convert the payload to JSON format
    cred = json.dumps(payload).encode('utf-8')

    # Set the headers for the POST request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    # Create a request object
    req = urllib.request.Request(url, data=cred, headers=headers, method='POST')
    try:
        # Make the POST request and retrieve the response
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                # Parse the response data
                response_data = json.loads(resp.read().decode('utf-8'))
                # Extract and return the token
                return response_data.get('token')
            else:
                raise Exception(f"Failed to retrieve token. Status code: {resp.status}")
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP Error: {e.code}, {e.reason}")


def dynamo_check_pk_exists(pk_bucket_key: str) -> bool:
    client_dynamo = boto3.client('dynamodb', region_name=REGION_AWS)
    print("dynamo_check_pk_exists:::", pk_bucket_key)
    try:
        # Check if partition key already exists in DynamoDB
        response_get = client_dynamo.get_item(
            TableName=DYNAMO_TABLE_TRACKER,
            Key={
                PARTITION_KEY_BUCKET_KEY: {'S': pk_bucket_key}
            }
        )
        print(response_get)
        if 'Item' in response_get:
            return True
    except Exception as e:
        raise Exception(f"An error occurred in dynamo_put_pk: {str(e)}")


def dynamo_put_pk(pk_bucket_key: str, folder_id: int, status: str) -> bool:
    """
    Add PK to DynamoDB.
    :param pk_bucket_key: Partition Key is the folder_id.
    :param folder_id: Partition Key is the folder_id.
    :param status: Partition Key is the folder_id.
    :return: DynamoDB response.
    """
    # Initialize the boto3 client for DynamoDB
    client_dynamo = boto3.client('dynamodb', region_name=REGION_AWS)
    try:
        # Check if partition key already exists in DynamoDB
        client_dynamo.put_item(
            TableName=DYNAMO_TABLE_TRACKER,
            Item={
                PARTITION_KEY_BUCKET_KEY: {'S': pk_bucket_key},
                ATTRIBUTE_FOLDER_ID: {'N': str(folder_id)},
                ATTRIBUTE_CREATED_AT: {'S': datetime.datetime.now().isoformat()},  # Current timestamp
                ATTRIBUTE_STATUS: {"S": status}
            }
        )
        return True
    except Exception as e:
        raise Exception(f"An error occurred in dynamo_put_pk: {str(e)}")


def send_to_sqs(folder_metadata_pdf):
    try:
        # Create SQS client
        sqs = boto3.client('sqs', region_name=os.getenv('REGION_AWS'))
        # Send a message to the queue
        queue_url = SQS_QUEUE_METADATA_PDF_URL
        print("QUEUEURL::", queue_url)
        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(folder_metadata_pdf)
        )
        return response['MessageId']
    except Exception as e:
        raise Exception(f"Failed to send message to SQS:::{str(e)}")


def send_folder_metadata(folder_id: int):
    POST_PATH = os.getenv('API_AI_AGENT_NAME_MAPPING_URL_POST_PATH')
    token_AI_AGENT_NAME_mapping = get_token()
    # Make the POST request to retrieve the token
    url = f"{os.getenv('API_AI_AGENT_NAME_MAPPING_URL')}/{POST_PATH}"
    headers = {
        'Content-Type': 'application/json',
        'Accepts': 'application/json',
        'Authorization': token_AI_AGENT_NAME_mapping
    }
    payload = {
        'folder_id': folder_id
    }
    folder_pl = json.dumps(payload).encode('utf-8')
    # Create a request object
    req = urllib.request.Request(url, data=folder_pl, headers=headers, method='POST')
    try:
        # Make the POST request and retrieve the response
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                # Parse the response data
                response_data = json.loads(resp.read().decode('utf-8'))
                print("ResponseData:::", response_data)
                # Construct the message to send to SQS
                message_ids: list = []
                for metadata in response_data:
                    print("DTT::", DYNAMO_TABLE_TRACKER)
                    print("PDF_ID ::", metadata.get('guid'))
                    if dynamo_check_pk_exists(pk_bucket_key=metadata.get('guid')):
                        print("PDF_ID ALREADY PROCESSED::", metadata.get('guid'))
                        continue
                    print("PDF_ID GUID::", metadata.get('guid'))
                    folder_metadata_pdf = ({
                        "folder_id": metadata.get('folder_id'),
                        "title": metadata.get('title', None),
                        "capture_time": metadata.get('capture_time', None),
                        "page_length": metadata.get('page_length', None),
                        "author": metadata.get('author', None),
                    })
                    message_id = send_to_sqs(folder_metadata_pdf)
                    message_ids.append(message_id)
                    # Dynamo Tracker - we need to record folder in table for checking status
                    dynamo_put_pk(pk_bucket_key=metadata.get('guid'), folder_id=folder_id, status=STATUS_IN_PROGRESS)
                    exit(1)
                return message_ids
            else:
                raise Exception(f"Failed to retrieve token. Status code: {resp.status}")
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP Error: {e.code}, {e.reason}")


def dynamo_check_status_get_items_by_gsi(folder_id: int) -> str:
    # Initialize the boto3 client for Dynamo
    # Initialize the boto3 client for DynamoDB
    client_dynamo = boto3.client('dynamodb', region_name=REGION_AWS)
    try:
        # Build the expression attribute values
        expression_attribute_values = {
            ':pk_val': {'N': str(folder_id)}
        }

        # Build the key condition expression
        key_condition_expression = f"{ATTRIBUTE_FOLDER_ID} = :pk_val"

        # Perform the query operation using the GSI
        response = client_dynamo.query(
            TableName=DYNAMO_TABLE_TRACKER,
            IndexName="FOLDER_ID_index",
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        items = response.get('Items', [])
        print("items::", items)
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = client_dynamo.query(
                TableName=DYNAMO_TABLE_TRACKER,
                IndexName="FOLDER_ID_index",
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))
            print("No body provided::")
        # Check if the 'STATUS' key is in the item and retrieve its value
        for item in items:
            if item.get('STATUS', {}).get('S') == STATUS_COMPLETED:
                continue
            if item.get('STATUS', {}).get('S') == STATUS_IN_PROGRESS:
                return STATUS_IN_PROGRESS
            if item.get('STATUS', {}).get('S') == STATUS_ERROR:
                return STATUS_ERROR
        return STATUS_COMPLETED
    except Exception as e:
        raise Exception("An error occurred in dynamo_add_attribute:::", str(e))


def lambda_handler(event, context=None):
    print("EVENT:::", event)
    # Parse the JSON body if it exists
    if event.get('body') is None:
        print("No body provided::")
        raise Exception('No body provided:::')
    if event['httpMethod'] == 'POST':
        if event.get('body'):
            try:
                parsed_body = json.loads(event.get('body', '{}'))
            except json.JSONDecodeError:
                raise Exception("Invalid JSON body:::")
            if parsed_body.get('folder_id') is None:
                raise Exception('No parameter folder_id provided:::')
            # Access specific fields from the body
            folder_id = parsed_body.get('folder_id')
            if not isinstance(folder_id, int):
                raise Exception('folder_id must be an integer:::')
            try:
                response_sqs_message_ids = send_folder_metadata(folder_id)
                print("MessageIds:::", response_sqs_message_ids)
                if response_sqs_message_ids is not None:
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'message': 'Success',
                            'input': event
                        })
                    }
            except Exception as e:
                raise Exception(f"Failed to send message to SQS:::{str(e)}")

    if event['httpMethod'] == 'GET':
        # Parse the JSON body if it exists
        if event.get('body'):
            try:
                parsed_body = json.loads(event.get('body', '{}'))
            except json.JSONDecodeError:
                raise Exception("Invalid JSON body:::")
            if parsed_body.get('folder_id') is None:
                raise Exception('No parameter folder_id provided:::')
            # Access specific fields from the body
            folder_id = parsed_body.get('folder_id')
            try:
                response_status = dynamo_check_status_get_items_by_gsi(folder_id)
                print("ResponseStatus dynamo_check_status_get_items_by_gsi:::", response_status)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'folder_id': folder_id,
                        'status': response_status,
                        'input': event
                    })
                }
            except Exception as e:
                raise Exception(f"Failed to send message to SQS:::{str(e)}")
