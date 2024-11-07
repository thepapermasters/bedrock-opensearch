import datetime

import boto3

from constants import ATTRIBUTE_STATUS, ATTRIBUTE_FINISHED_AT, DYNAMO_TABLE_TRACKER, PARTITION_KEY_BUCKET_KEY, \
    REGION_AWS


def dynamo_put_status_finished(pk_bucket_key: str, status: str) -> bool:
    """
    Add PK to DynamoDB.
    :param pk_bucket_key: Partition Key is the folder_id.
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
                ATTRIBUTE_FINISHED_AT: {'S': datetime.datetime.now().isoformat()},
                ATTRIBUTE_STATUS: {'S': status}
            }
        )
        return True
    except Exception as e:
        raise Exception(f"An error occurred in dynamo_add_attribute: {str(e)}")
