import json
import os

import boto3


def send_to_dlq(dlq_url, message_body):
    """
      Example usage
        message_body = "failed message content"
        dlq_url = 'https://sqs.us-east-1.amazonaws.com/[aws account id]/[dlq_name]'
        send_to_dlq(message_body, dlq_url)
    """
    try:
        # Create SQS client
        sqs = boto3.client('sqs', region_name=os.getenv('REGION_AWS'))
        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=dlq_url,
            MessageBody=json.dumps(message_body)
        )
        return response['MessageId']
    except Exception as e:
        raise Exception(f"Failed to send message to SQS:::{str(e)}")
