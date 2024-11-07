import json
import os

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


def send_question_to_os(folder_id: int, question: str, memory_id: str = None, ai_context: str="Image Analyst for the USPTO") -> dict:
    # Create OpenSearch client
    client_op = boto3.client('opensearch', region_name=os.getenv('REGION_AWS'))

    search_query = {
        "query": {
            "match": {
                "capture_summary.folder_id": folder_id
            },
            "parameters": {
                "question": question,
                "memory_id": memory_id,
                "message_history_limit": 5,
                "prompt": "Human: You are an ${ai_context}. You will always answer questions based on "
                          "the given context. If the answer is not directly shown in the context, "
                          "you will analyze the image_binary and find the answer. If you don't know the answer, "
                          "say 'I can not find data matching your request.'"
                          "'\n\nContext:\n${parameters.population_knowledge_base.output:-}\n\n${"
                          "parameters.chat_history:-}\n\nHuman: Always learn useful information from chat "
                          "history.\nHuman: ${parameters.question}, ${parameters.next_action}\n\nAssistant:"
            }
        }
    }

    # Convert the query to a JSON string
    search_query_json = json.dumps(search_query)
    try:
        # Execute the search request
        response = client_op.search(
            DomainName=os.getenv("OPENSEARCH_DOMAIN_NAME"),
            IndexName=os.getenv("OPENSEARCH_INDEX_NAME"),
            Body=search_query_json
        )

        # Initialize variables to store memory ID and answer
        memory_id = None
        answer = None

        # Check if response contains hits and extract necessary fields
        if 'hits' in response and 'hits' in response['hits']:
            for hit in response['hits']['hits']:
                # Assuming the response contains relevant fields in `_source`
                source = hit['_source']
                # Extract relevant fields based on the structure of your documents
                memory_id = source.get('memory_id', memory_id)
                answer = source.get('answer', 'No data found matching your request.')

        return {"response": answer, "memory_id": memory_id}

    except (ClientError, Exception) as e:
        raise Exception(f"Failed ClientError:::{str(e)}")
    except NoCredentialsError as e:
        print("AWS credentials not found.")
        raise Exception(f"Failed NoCredentialsError:::{str(e)}")
    except PartialCredentialsError as e:
        print("AWS credentials are incomplete.")
        raise Exception(f"Failed PartialCredentialsError:::{str(e)}")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise Exception(f"Failed send_question_to_os:::{str(e)}")


def lambda_handler(event, context=None):
    print("EVENT:::", event)
    # Parse the JSON body if it exists
    if event.get('body') is None:
        raise Exception('No body provided:::')
    # if event['httpMethod'] == 'POST':
    if event.get('body'):
        try:
            parsed_body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            raise Exception("Invalid JSON body:::")
        if parsed_body.get('memory_id'):
            memory_id = parsed_body.get('memory_id')
        else:
            memory_id = None
        if parsed_body.get('folder_id') is None:
            raise Exception('No parameter folder_id provided:::')
        # Access specific fields from the body
        folder_id = parsed_body.get('folder_id')
        if not isinstance(folder_id, int):
            raise Exception(f'folder_id must be an integer:::{folder_id}')
        if parsed_body.get('question') is None:
            raise Exception('No parameter question provided:::')
            # Access specific fields from the body
        question = parsed_body.get('question')
        if not isinstance(question, str):
            raise Exception(f'question must be a string:::{question}')
        try:
            response_answer = send_question_to_os(folder_id, question, memory_id)
            print("Answer:::", response_answer)
            if response_answer is not None:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'folder_id': folder_id,
                        'question': question,
                        'answer': response_answer,
                        'memory_id': memory_id,
                        'input': event
                    })
                }
        except Exception as e:
            raise Exception(f"Failed to send question to OpenSearch:::{str(e)}")
