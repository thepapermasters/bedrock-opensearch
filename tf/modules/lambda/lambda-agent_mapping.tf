# Creates the zip file of lambda code
data "archive_file" "archive_lambda_AI_AGENT_NAME_mapping" {
  type        = "zip"
  source_file = "${path.module}/AI_AGENT_NAME_mapping.py"
  output_path = "${path.module}/AI_AGENT_NAME_mapping.zip"
}

# Uploads the zip file to S3 bucket
resource "aws_s3_object" "s3object_lambda_AI_AGENT_NAME_mapping" {
  bucket      = var.s3bucket_lambda_code_var_id
  key         = "lambda-AI_AGENT_NAME-mapping.zip"
  source      = data.archive_file.archive_lambda_AI_AGENT_NAME_mapping.output_path
  source_hash = data.archive_file.archive_lambda_AI_AGENT_NAME_mapping.output_base64sha256
}


# Creates the lambda function
resource "aws_lambda_function" "lambda_AI_AGENT_NAME_mapping" {
  function_name    = local.lambda_AI_AGENT_NAME_mapping_var
  description      = "Lambda for PV AI_AGENT_NAME-mapping endpoint."
  role             = local.lambda_role_to_rule_them_all_var_arn
  s3_bucket        = var.s3bucket_lambda_code_var_id
  s3_key           = aws_s3_object.s3object_lambda_AI_AGENT_NAME_mapping.key
  handler          = "AI_AGENT_NAME_mapping.lambda_handler"
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 512
  source_code_hash = data.archive_file.archive_lambda_AI_AGENT_NAME_mapping.output_base64sha256
  environment {
    variables = {
      API_AI_AGENT_NAME_MAPPING_URL           = var.API_AI_AGENT_NAME_MAPPING_URL
      API_AI_AGENT_NAME_MAPPING_USER          = var.API_AI_AGENT_NAME_MAPPING_USER
      API_AI_AGENT_NAME_MAPPING_PASSWORD      = var.API_AI_AGENT_NAME_MAPPING_PASSWORD
      API_AI_AGENT_NAME_MAPPING_URL_POST_PATH = var.API_AI_AGENT_NAME_MAPPING_PASSWORD
      DYNAMO_TABLE_TRACKER           = var.dynamo_tracker_var_arn
      SQS_QUEUE_METADATA_PDF_URL     = var.queue_metadata_pdf_var_url
      REGION_AWS                     = var.region_var
    }
  }
  tags = merge(
    var.localTags,
    tomap({ "Name" = local.lambda_AI_AGENT_NAME_mapping_var })
  )
}

resource "aws_lambda_permission" "allow_api_gateway_AI_AGENT_NAME_mapping" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_AI_AGENT_NAME_mapping.function_name
  principal     = "apigateway.amazonaws.com"
}


