import json

import urllib3

from constants import PIPELINE_NAME, OPENSEARCH_INDEX_NAME

opensearch_conn_timeout = 600
http = urllib3.PoolManager()

# opensearch_url = OPENSEARCH_DOMAIN_ENDPOINT
opensearch_url = "http://localhost:9200"
simulate_pipeline = {
    "docs": [
        {
            "_index": OPENSEARCH_INDEX_NAME,
            "_id": "1",
            "_source": {
                "id": "testid01",
                "capture_summary_json": json.dumps({"model": "test", 'value': "test2"})
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
