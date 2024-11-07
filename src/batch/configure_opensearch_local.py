import json
import time

import boto3
import urllib3
from botocore.exceptions import ClientError

from constants import OPENSEARCH_DOMAIN_ENDPOINT, REGION_AWS
from constants import OPENSEARCH_DOMAIN_NAME

print("Getting in HERE:::")

# Initialize the Boto3 client for OpenSearch
client_os = boto3.client('opensearch', region_name=REGION_AWS)
opensearch_domain_endpoint = OPENSEARCH_DOMAIN_ENDPOINT

http = urllib3.PoolManager()


def check_opensearch_health(timeout=60, client_boto3=client_os) -> bool:
    up_and_running = False
    count = 0

    while not up_and_running and count < timeout:
        try:
            # Describe the OpenSearch domain to get domain status
            response = client_boto3.describe_domain(DomainName=OPENSEARCH_DOMAIN_NAME)
            domain_status = response['DomainStatus']
            print("Getting in check_opensearch_health response:::", response)
            # Check if the domain status is active and there is an endpoint available
            if domain_status['Processing'] is False and 'Endpoint' in domain_status:
                print(f"OpenSearch domain is active. Checking endpoint health...")

                # Retrieve the cluster health by making a signed HTTP request using boto3
                cluster_health = client_boto3.list_domain_names()  # Can be replaced with more specific domain health checks
                if cluster_health['DomainNames']:
                    up_and_running = True
                    print(f"Cluster Health Check Passed for domain: {OPENSEARCH_DOMAIN_NAME}")
                    return True
            else:
                print(f"Domain is still processing or no endpoint is available.")

        except ClientError as e:
            print(f"Error describing domain: {e}")
            if count >= timeout:
                break
        except Exception as e:
            print(f"Unexpected error: {e}")

        print("⏰ Waiting for OpenSearch to start...")
        count += 1
        time.sleep(1)

    if not up_and_running:
        print("OpenSearch is not running. Please start it up and try again.")
        return False


# Use the function to check OpenSearch health
if not check_opensearch_health(client_boto3=client_os):
    exit(1)
else:
    print("OpenSearch is up and running.")


# Function to check if the OpenSearch ML plugin is initialized
def check_ml_plugin_initialized(client_boto3=client_os, timeout=30) -> bool:
    """
    Check if the OpenSearch ML plugin is initialized using boto3 only.
    This function verifies the domain's overall status and configuration to determine if the ML plugin is active.
    """
    ml_plugin_initialized = False
    count = 0

    while not ml_plugin_initialized and count < timeout:
        try:
            # Describe the OpenSearch domain to get domain status and configurations
            response = client_boto3.describe_domain(DomainName=OPENSEARCH_DOMAIN_NAME)
            domain_status = response['DomainStatus']
            print("Getting in ml_plugin_initialized response:::", response)
            # Check if domain is active and configurations are loaded
            if not domain_status['Processing'] and 'Endpoint' in domain_status:
                print("Domain is active and available.")

                # Check for ML plugin configurations (if present in AdvancedOptions or other domain configurations)
                if 'AdvancedOptions' in domain_status:
                    advanced_options = domain_status['AdvancedOptions']
                    # Example check for an ML plugin-related configuration in AdvancedOptions
                    if advanced_options.get('plugins.ml_commons.only_run_on_ml_node') is not None:
                        ml_plugin_initialized = True
                        print("ML Plugin appears to be configured and initialized.")
            else:
                print("Domain is still processing or endpoint is unavailable.")

        except ClientError as e:
            print(f"Error describing domain: {e}")
            break  # Break the loop on client error
        except Exception as e:
            print(f"Unexpected error: {e}")

        # If not initialized, wait for 1 second and retry
        if not ml_plugin_initialized:
            print("⏰ Waiting for the ML plugin to initialize...")
            count += 1
            time.sleep(1)

    if ml_plugin_initialized:
        print("ML Plugin is initialized.")
    else:
        print("ML Plugin is not initialized. Please check the configuration.")

    return ml_plugin_initialized


# Check if the ML plugin is initialized using the function
if not check_ml_plugin_initialized():
    print("ML Plugin is not running. Exiting...")
    exit(1)
else:
    print("ML Plugin is running and initialized.")

# Cluster settings - Configure required persistent settings
persistent_settings = {
    "persistent": {
        "plugins": {
            "ml_commons": {
                "only_run_on_ml_node": True,  # test this line
                "model_access_control_enabled": True,
                "native_memory_threshold": 99
            }
        }
    }
}

cs = json.loads(http.request(
    'POST',
    OPENSEARCH_DOMAIN_ENDPOINT + "/_cluster/settings",
    body=json.dumps(persistent_settings)
).data.decode('utf-8'))

# Register model group
model_group = {
    "name": "all_models_model_group",
    "description": "A model group for all registered models",
}
exit(1)
print("Searching for Existing Models")
search_models = json.loads(http.request(
    'POST',
    opensearch_url + "/_plugins/_ml/models/_search",
    headers={'Content-Type': 'application/json'},
    body=json.dumps({
        "query": {
            "match_all": {}
        },
        "size": 1000
    })).data.decode('utf-8'))
print(search_models)
print("Clearing Models..")
for model in search_models["hits"]["hits"]:
    mid = model["_id"]
    print("MODEL TO DELETE::", mid)
    udeploy = json.loads(http.request(
        'POST',
        opensearch_url + f"/_plugins/_ml/models/{mid}/_undeploy").data.decode('utf-8'))
    print(udeploy)
    delmodel = json.loads(http.request(
        'DELETE',
        opensearch_url + f"/_plugins/_ml/models/{mid}").data.decode('utf-8'))
    print(delmodel)
print("Searching for Existing Model Groups")
search_groups = json.loads(http.request(
    'POST',
    opensearch_url + "/_plugins/_ml/model_groups/_search",
    headers={'Content-Type': 'application/json'},
    body=json.dumps({
        "query": {
            "match_all": {}
        },
        "size": 1000
    })).data.decode('utf-8'))
print(search_groups)
print("Clearing Models Groups..")
for model in search_groups["hits"]["hits"]:
    print('GROUP::', model)
    mid = model["_id"]
    # udeploy = requests.post(opensearch_url + f"/_plugins/_ml/model_groups/{mid}/_undeploy")
    res = json.loads(http.request(
        'DELETE',
        opensearch_url + f"/_plugins/_ml/model_groups/{mid}",
        headers={'Content-Type': 'application/json'},
        body=json.dumps({
            "query": {
                "match_all": {}
            },
            "size": 1000
        })).data.decode('utf-8'))
    print('RES::', res)
print("Registering Model Group...")
response_register_group = json.loads(http.request(
    'POST',
    opensearch_url + "/_plugins/_ml/model_groups/_register",
    headers={'Content-Type': 'application/json'},
    body=json.dumps(model_group)).data.decode('utf-8'))

print(f"response_register_group:::{response_register_group}")

model_group_id = response_register_group["model_group_id"]
# Register HF Embeddings model https://opensearch.org/docs/latest/ml-commons-plugin/pretrained-models/
embeddings_model = {
    "name": MODEL_EMBEDDING_NAME,
    "version": MODEL_EMBEDDING_NAME_VERSION,
    "model_group_id": model_group_id,
    "model_format": "TORCH_SCRIPT",
    "model_task_type": "TEXT_EMBEDDING",
}

print("Registering Model...")
response_register_model = json.loads(http.request(
    'POST',
    opensearch_url + "/_plugins/_ml/models/_register?deploy=true",
    headers={'Content-Type': 'application/json'},
    body=json.dumps(embeddings_model)).data.decode('utf-8'))
print(response_register_model)
# print(response_register.json())
taskid = response_register_model['task_id']
model_id_embedding = None
retry_count = 0
time.sleep(3)
while model_id_embedding is None:
    response_task_info = json.loads(http.request(
        'GET',
        opensearch_url + f"/_plugins/_ml/tasks/{taskid}").data.decode('utf-8'))
    state = response_task_info['state']
    print("Model Registered State::", state)
    if state == 'COMPLETED':
        model_id_embedding = response_task_info['model_id']
        deployed = True
    time.sleep(1)
    retry_count += 1
    if (retry_count > 60):
        print("Timeout while deploying model")
        exit(1)

model_is_deployed = False
retry_count = 0
while not model_is_deployed:
    response_validate_model = json.loads(http.request(
        'GET',
        opensearch_url + f"/_plugins/_ml/models/{model_id_embedding}",
        headers={'Content-Type': 'application/json'},
    ).data.decode('utf-8'))
    print(response_validate_model)
    print("Model Deployed State::", response_validate_model['model_state'])
    if response_validate_model['model_state'] == 'DEPLOYED':
        model_is_deployed = True
    time.sleep(1)
    retry_count += 1
    if (retry_count > 60):
        print("Timeout Deploying Model")
        exit(1)
print(f"Model Deployed with model_id_embedding: {model_id_embedding}")
print("Create Embedding Pipeline")
# Create Pipeline
pipeline = {
    "description": "A text/image embedding pipeline",
    "processors": [
        {
            "text_image_embedding": {
                "model_id": model_id_embedding,
                "embedding": "vector_embedding",
                "field_map": {
                    "capture_summary_json": "capture_summary_json_embedding",
                    "page_summary_json": "page_summary_json_embedding",
                    "image_binary": "image_binary_embedding",
                }
            }
        }
    ]
}
response_pipeline = json.loads(http.request(
    'PUT',
    opensearch_url + f"/_ingest/pipeline/{PIPELINE_NAME}",
    headers={'Content-Type': 'application/json'},
    body=json.dumps(pipeline)).data.decode('utf-8'))
print(response_pipeline)
print("SIMULATE PIPELINE")
# Simulate Pipeline
simulate_pipeline = {
    "docs": [
        {
            "_index": OPENSEARCH_INDEX_NAME,
            "_id": "1",
            "_source": {
                "id": "testid01",
                "capture_summary_json": "This is a demo text that will generate the embeddings",
                "page_summary_json": "This is a demo text that will generate the embeddings",
                "image_binary": "image_binary_embedding"
            }
        }
    ]
}

response_simulate_pipeline = json.loads(http.request(
    'POST',
    opensearch_url + f"/_ingest/pipeline/{PIPELINE_NAME}/_simulate",
    headers={'Content-Type': 'application/json'},
    body=json.dumps(simulate_pipeline)).data.decode(
    'utf-8'))
print(response_simulate_pipeline)
print("Create Index and Assign Pipeline")
# Create Index and Assign Pipeline

print("Drop Index if it Exists")
dropped = json.loads(http.request(
    'DELETE',
    opensearch_url + "/" + OPENSEARCH_INDEX_NAME).data.decode(
    'utf-8'))

print(dropped)
print("Create Index")
# create_op_index()

create_index = {
    "settings": {
        "index.knn": True,
        "default_pipeline": PIPELINE_NAME,
        "number_of_shards": 2
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "page_name": {"type": "text"},
            "image_binary": {"type": "binary"},
            "image_binary_embedding": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                    "engine": "lucene",
                    "space_type": "l2",
                    "name": "hnsw",
                    "parameters": {}
                }
            },
            "location": {
                "properties": {
                    "bucket_name_pdf": {"type": "keyword"},
                    "bucket_key_pdf": {"type": "keyword"},
                    "bucket_name_raw_image": {"type": "keyword"},
                    "bucket_key_raw_image": {"type": "keyword"}
                }
            },
            "capture_summary_json_embedding": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                    "engine": "lucene",
                    "space_type": "l2",
                    "name": "hnsw",
                    "parameters": {}
                }
            },
            "capture_summary_json": {"type": "text"},
            "capture_summary": {
                "properties": {
                    "folder_id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "capture_time": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
                    "page_length": {"type": "integer"},
                    "author": {"type": "text"}
                }
            },
            "page_summary_json": {"type": "text"},
            "page_summary_json_embedding": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                    "engine": "lucene",
                    "space_type": "l2",
                    "name": "hnsw",
                    "parameters": {}
                }
            },
            "page_summary": {
                "properties": {
                    "summary": {"type": "text"},
                    "logo": {"type": "text"},
                    "weapon": {"type": "text"},
                    "physical_features": {"type": "text"},
                    "physical_activity": {"type": "text"},
                    "false_advertising": {"type": "text"},
                    "patent": {"type": "text"},
                    "intellectual_property": {"type": "text"},
                    "trademark": {"type": "text"},
                    "copyright": {"type": "text"},
                    "trade_secret": {"type": "text"},
                    "infringement": {"type": "text"},
                    "product": {"type": "text"},
                    "sales": {"type": "text"},
                    "liability": {"type": "text"},
                    "criminal": {"type": "text"},
                    "defamation": {"type": "text"},
                    "slander": {"type": "text"},
                    "text": {"type": "text"},
                    "other": {"type": "text"}
                }
            }
        }
    }
}
print("Creating OS Index...")
response_create_index = json.loads(http.request(
    'PUT',
    opensearch_url + "/" + OPENSEARCH_INDEX_NAME,
    headers={'Content-Type': 'application/json'},
    body=json.dumps(create_index)

).data.decode('utf-8'))

print(response_create_index)

print("Testing Embeddings")

print("ADD DOCUMENT")

# Get docR
add_doc = {
    "id": "document0001",
    "image_description": "Orange table",
    "image_binary": "iVBORw0KGgoAAAANSUI...",
    'capture_summary_json': json.dumps({
        "folder_id": "metadata.folder_id",
        "title": "metadata.title",
        "page_length": "metadata.page_length",
        "author": "metadata.author"
    }),
    "capture_summary": {
        "folder_id": "metadata.folder_id",
        "title": "metadata.title",
        "page_length": 1,
        "author": "metadata.author"
    }
}
print("Adding Document...")
response_add_doc_sparse_encoding = json.loads(http.request(
    'POST',
    f"{opensearch_url}/{OPENSEARCH_INDEX_NAME}/_doc/1?refresh=wait_for",
    headers={'Content-Type': 'application/json'},
    body=json.dumps(add_doc)).data.decode('utf-8'))
print("response_add_doc_sparse_encoding::", response_add_doc_sparse_encoding)
response_get_doc = json.loads(http.request(
    'GET',
    f"{opensearch_url}/{OPENSEARCH_INDEX_NAME}/_doc/1",
    headers={'Content-Type': 'application/json'}).data.decode('utf-8'))

print('GET - Check if document has the embeddings filled in:::', response_get_doc)
print("Embeddings Found::", len(response_get_doc['_source']['capture_summary_json_embedding']))

# Search doc
search_doc = {
    "_source": {
        "excludes": [
            "capture_summary_json_embedding"
        ]
    },
    "query": {
        "neural": {
            "image_binary_embedding": {
                "query_text": "person dancing",
                "query_image": "iVBORw0KGgoAAAANSUI...",
                "model_id": model_id_embedding,
                "k": 5
            },
            "capture_summary_json_embedding": {
                "query_text": "person dancing",
                "model_id": model_id_embedding,
                "k": 5
            },
            "page_summary_json_embedding": {
                "query_text": "person dancing",
                "model_id": model_id_embedding,
                "k": 5
            }
        }
    }
}

print(
    f"##### Please add MODEL_ID_EMBEDDING::: {model_id_embedding} and the MODEL_GROUP_ID::: {model_group_id} to the 'constants.py' file. #####")
print('Delete the test doument from OS:::', search_doc)
response_get_doc = json.loads(http.request(
    'DELETE',
    f"{opensearch_url}/{OPENSEARCH_INDEX_NAME}/_doc/1",
    headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
