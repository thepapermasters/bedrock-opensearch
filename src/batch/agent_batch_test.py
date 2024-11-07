import json

from batch.AI_AGENT_NAME_batch import process_event

test_event_json = json.dumps(test_event)
print(test_event_json)
event = {
    "Records": [
        {
            "messageId": "12345678-1234-5678-1234-567812345678",
            "receiptHandle": "AQEB12345Example",
            "body": test_event_json,
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "125486745",
                "SenderId": "2345785412",
                "ApproximateFirstReceiveTimestamp": "37245757454"
            },
            "messageAttributes": {},
            "md5OfBody": "435GDF45GDF45DGF456FG",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-1:[AWS_ACCOUNT]:MyQueue",
            "awsRegion": "us-east-1"
        }
    ]
}

print(event)

process_event(event=event)
