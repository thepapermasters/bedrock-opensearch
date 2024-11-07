# Constants AWS
import os

from utils.get_env import get_env

REGION_AWS = os.getenv("REGION_AWS")

# Constants - Dynamo
DYNAMO_TABLE_TRACKER = get_env("DYNAMO_TABLE_TRACKER")
PARTITION_KEY_BUCKET_KEY = "BUCKET_KEY"
ATTRIBUTE_FOLDER_ID = "FOLDER_ID"
ATTRIBUTE_CREATED_AT = "CREATED_AT"
ATTRIBUTE_STATUS = "STATUS"
ATTRIBUTE_FINISHED_AT = "FINISHED_AT"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_COMPLETED = "COMPLETED"
STATUS_ERROR = "ERROR"

# Constants - OpenSearch
OPENSEARCH_DOMAIN_NAME = get_env("OPENSEARCH_DOMAIN_NAME")
OPENSEARCH_DOMAIN_ENDPOINT = get_env("OPENSEARCH_DOMAIN_ENDPOINT")
OP_PORT: int = 443
OPENSEARCH_INDEX_NAME = "AI_AGENT_NAME"
# MODEL_LLM= "anthropic.claude-3-opus-20240229-v1:0"
MODEL_LLM = "anthropic.claude-3-5-sonnet-20240620-v1:0"  # Claude 3.5 Sonnet, which can handle up to 200,000 tokens for the input context window, equivalent to approximately 800,000 bytes (or around 800 KB)
TEMPERATURE = 0

# Opensearch embeddings model
MODEL_GROUP_ID = "goXVR5IBp8eTDvQ42KVi"
MODEL_GROUP_NAME = 'all_models_model_group'
MODEL_EMBEDDING_NAME = 'huggingface/sentence-transformers/msmarco-distilbert-base-tas-b'
# MODEL_EMBEDDING_NAME = 'openai/clip-vit-base-patch32'
MODEL_EMBEDDING_NAME_VERSION = '1.0.2'

# LLM_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
# INGEST_LLM_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"  # model to generate metadata per image


MODEL_ID_EMBEDDING = 'hIXVR5IBp8eTDvQ42qVm'
CONTENT_TYPE_JSON = 'application/json'
PIPELINE_NAME = 'AI_AGENT_NAME-ingest-pipeline'
MODEL_AGENT_ID = 'sIXVR5IBp8eTDvQ42qVn'

# Constants - S3
BUCKET_NAME_RAW_IMAGES = get_env("BUCKET_NAME_RAW_IMAGES")
BUCKET_RAW_PDFS = get_env("BUCKET_RAW_PDFS")

# Constants - SQS
SQS_QUEUE_METADATA_PDF_URL = os.getenv("SQS_QUEUE_METADATA_PDF_URL")
SQS_DLQ_METADATA_PDF_URL = os.getenv("SQS_DLQ_METADATA_PDF_URL")
