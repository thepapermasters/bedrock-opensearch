from dotenv import load_dotenv

load_dotenv()

from AI_AGENT_NAME_mapping import lambda_handler

event = {
    "body": "{\"folder_id\": 123}",
    "httpMethod": "POST"
}
lambda_handler(event)

