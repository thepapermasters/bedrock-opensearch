from dotenv import load_dotenv

load_dotenv()

from AI_AGENT_NAME_q_a import lambda_handler

event = {
    "body": "{\"folder_id\": 123, \"question\": \"Is someone running in these images?\"}",
    "httpMethod": "POST"
}
lambda_handler(event)
