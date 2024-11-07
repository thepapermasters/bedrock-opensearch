# Initialize the SQS client
import boto3

from constants import SQS_QUEUE_METADATA_PDF_URL


def sqs_message_delete(receipt_handle: str) -> None:
    # Create SQS client
    sqs = boto3.client('sqs')

    # The URL of SQS queue
    queue_url = SQS_QUEUE_METADATA_PDF_URL

    # Delete the message
    response = sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )

    return response
