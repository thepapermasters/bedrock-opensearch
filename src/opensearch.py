import time

import boto3
from botocore.exceptions import ClientError

from constants import REGION_AWS, OPENSEARCH_INDEX_NAME


##################### AWS Resources #####################


def check_status_os(domain_name: str) -> bool:
    """
    Check the status of an OpenSearch domain and wait for it to be ready (yellow or green).

    Args:
        domain_name (str): The name of the OpenSearch domain to check.

    Returns:
        bool: True if the OpenSearch domain is up and running (yellow or green), False otherwise.
    """
    # Initialize the boto3 client for OpenSearch
    client_os = boto3.client('opensearch')
    up_and_running = False
    opensearch_conn_timeout = 600

    try:
        # Check the cluster health
        response = client_os.describe_domain_health(DomainName=domain_name)
        cluster_status = response.get('DomainStatus', {}).get('ClusterHealth', None)
        print(f"RESPONSE - Working: {response}")

        # Check if the cluster status is yellow or green
        if cluster_status in ["YELLOW", "GREEN"]:
            up_and_running = True

    except ClientError as e:
        raise Exception("Client error occurred in check_status_os:::", str(e))

    # If not up and running, enter a wait loop
    if not up_and_running:
        count = 0
        while not up_and_running and count < opensearch_conn_timeout:
            print("⏰ Waiting for OpenSearch to start...")
            time.sleep(1)
            count += 1
            try:
                # Retry checking the cluster health
                response = client_os.describe_domain_health(DomainName=domain_name)
                cluster_status = response.get('DomainStatus', {}).get('ClusterHealth', None)

                # If the cluster status is yellow or green, set up_and_running to True
                if cluster_status in ["YELLOW", "GREEN"]:
                    up_and_running = True
                    print("Status:::", cluster_status)

            except ClientError as e:
                raise Exception("Client error occurred in check_status_os up_and_running:::", str(e))

    if not up_and_running:
        print("OpenSearch is not running. Please start it up and try again.")
        return False
    return True


def check_index_exists(os_domain_name: str) -> bool:
    client = boto3.client('opensearch', region_name=REGION_AWS)
    try:
        response = client.indices.exists(Index=os_domain_name)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False
    except client.exceptions.ResourceNotFoundException:
        return False


# Function to submit a document to OpenSearch
def submit_to_os(document_object) -> bool:
    # Initialize the boto3 client for OpenSearch
    client_os = boto3.client('opensearch', region_name=REGION_AWS)

    try:
        # Submit the document to the index
        response = client_os.index(
            index=OPENSEARCH_INDEX_NAME,
            id=document_object['id'],
            body=document_object
        )
        # Check if the request was successful
        if response['ResponseMetadata']['HTTPStatusCode'] in [200, 201]:
            return True
    except Exception as e:
        print(f"Error indexing document: {e}")

    return False
