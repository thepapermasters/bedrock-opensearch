import boto3
from botocore.exceptions import ClientError


def check_image_exists(bucket_name, object_key):
    client_s3 = boto3.client('s3')
    try:
        # Try to fetch the metadata of the object
        client_s3.head_object(Bucket=bucket_name, Key=object_key)
        print(f"Image '{object_key}' exists in bucket '{bucket_name}'.")
        return True
    except ClientError as e:
        # If a 404 error is raised, the object does not exist
        if e.response['Error']['Code'] == '404':
            print(f"Image '{object_key}' does not exist in bucket '{bucket_name}'.")
            return False


def upload_image_to_s3(bucket_name, bucket_key, image) -> bool:
    """
    Uploads an image to an S3 bucket.
    :param bucket_name:
    :param bucket_key: must be uri decoded
    :param image:
    :return: None
    """
    # Initialize boto3 clients
    client_s3 = boto3.client('s3')
    try:
        # Upload the image to S3
        client_s3.upload_fileobj(image, bucket_name, bucket_key)
        return True
    except Exception as e:
        raise Exception("An error occurred in upload_image_to_s3:::", str(e))
