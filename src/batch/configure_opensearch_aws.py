import json
import os
import time

import urllib3

from constants import MODEL_EMBEDDING_NAME, MODEL_EMBEDDING_NAME_VERSION, OPENSEARCH_INDEX_NAME, PIPELINE_NAME

# print("Getting in HERE:::")

# client = boto3.client('opensearch', region_name=REGION_AWS)

# Get domain information
# response = client.describe_domain(DomainName=OPENSEARCH_DOMAIN_NAME)
# Extract the endpoint from the response
# opensearch_url = response['DomainStatus']['Endpoint']

os.environ['REGION_AWS'] = 'us-east-1'
# opensearch_url = OPENSEARCH_DOMAIN_ENDPOINT
opensearch_url = "http://localhost:9200"

## Check if OpenSearch is up and running
up_and_running = False
opensearch_conn_timeout = 60
http = urllib3.PoolManager()

try:
    response = http.request(
        'GET',
        opensearch_url + "/_cluster/health",
    )
    print(f"RESPONSE - Working:::{response.status}")
    rdata = json.loads(response.data.decode('utf-8'))
    exit(0)
    if response.status == 200 and (rdata["status"] == "yellow" or rdata["status"] == "green"):
        up_and_running = True
except:
    if not up_and_running:
        count = 0
        while not up_and_running and count < opensearch_conn_timeout:
            print("⏰ Waiting for OpenSearch to start...")
            time.sleep(1)
            count += 1
            try:
                response = http.request(
                    'GET',
                    opensearch_url + "/_cluster/health",
                )
                print(f"RESPONSE Status:::{response.status}")
                rdata = json.loads(response.data.decode('utf-8'))
                if response.status == 200 and (
                        rdata["status"] == "yellow" or rdata["status"] == "green"):
                    up_and_running = True
                    print("Status:::", rdata["status"])
            except Exception as e:
                print(e)
                continue
if not up_and_running:
    print("OpenSearch is not running. Please start it up and try again.")
    exit(1)

# Wait until the ML plugin is initialized
ml_plugin_initialized = False
ml_plugin_timeout = 30
response = http.request(
    'GET',
    opensearch_url + "/.plugins-ml-config")
rdata = json.loads(response.data.decode('utf-8'))
print("rdata", rdata)
print(response.status)

if response.status == 200:
    ml_plugin_initialized = True
else:
    count = 0
    while not ml_plugin_initialized and count < ml_plugin_timeout:
        print("⏰ Waiting for the ML plugin to initialize...")
        time.sleep(1)
        count += 1
        try:
            response = http.request(
                'GET',
                opensearch_url + "/.plugins-ml-config")
            rdata = json.loads(response.data.decode('utf-8'))
            if response.status == 200:
                ml_plugin_initialized = True
        except:
            continue

if not ml_plugin_initialized:
    print("OpenSearch ML plugin is not initialized. Please check the issue.")
    exit(1)

# Cluster settings - Configure required persistent settings
persistent_settings = {
    "persistent": {
        "plugins": {
            "ml_commons": {
                "only_run_on_ml_node": False,  # test this line
                "model_access_control_enabled": True,
                "native_memory_threshold": 99
            }
        }
    }
}

cs = json.loads(http.request(
    'POST',
    opensearch_url + "/_cluster/settings",
    body=json.dumps(persistent_settings)
).data.decode('utf-8'))

# Register model group
model_group = {
    "name": "all_models_model_group",
    "description": "A model group for all registered models",
}

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
                    "id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "capture_time": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
                    "item_id": {"type": "keyword"},
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
        "id": "metadata.id",
        "title": "metadata.title",
        "item_id": "metadata.item_id",
        "page_length": "metadata.page_length",
        "author": "metadata.author"
    }),
    "capture_summary": {
        "folder_id": "metadata.folder_id",
        "id": "etadata.id",
        "title": "metadata.title",
        "item_id": "metadata.item_id",
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
# print("Embeddings Found::", len(response_get_doc['_source']['capture_summary_json_embedding']))

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
                "k": 3
            },
            "capture_summary_json_embedding": {
                "query_text": "person dancing",
                "model_id": model_id_embedding,
                "k": 3
            },
            "page_summary_json_embedding": {
                "query_text": "person dancing",
                "model_id": model_id_embedding,
                "k": 3
            }
        }
    }
}

print(
    f"##### Please add MODEL_ID_EMBEDDING::: {model_id_embedding} and the MODEL_GROUP_ID::: {model_group_id} to the 'constants.py' file. #####")
print('Delete the test document from OS:::', search_doc)
response_get_doc = json.loads(http.request(
    'DELETE',
    f"{opensearch_url}/{OPENSEARCH_INDEX_NAME}/_doc/1",
    headers={'Content-Type': 'application/json'}).data.decode('utf-8'))
