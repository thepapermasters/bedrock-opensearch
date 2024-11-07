# Creates the zip file of lambda code
data "archive_file" "archive_lambda_AI_AGENT_NAME_q_a" {
  type        = "zip"
  source_file = "${path.module}/AI_AGENT_NAME_q_a.py"
  output_path = "${path.module}/AI_AGENT_NAME_q_a.zip"
}

# Uploads the zip file to S3 bucket
resource "aws_s3_object" "s3object_lambda_AI_AGENT_NAME_q_a" {
  bucket      = var.s3bucket_lambda_code_var_id
  key         = "lambda-AI_AGENT_NAME-q_a.zip"
  source      = data.archive_file.archive_lambda_AI_AGENT_NAME_q_a.output_path
  source_hash = data.archive_file.archive_lambda_AI_AGENT_NAME_q_a.output_base64sha256
}

# Creates the lambda function
resource "aws_lambda_function" "lambda_AI_AGENT_NAME_q_a" {
  function_name    = local.lambda_AI_AGENT_NAME_q_a_var
  description      = "Lambda for PV AI_AGENT_NAME-q_a endpoint."
  role             = local.lambda_role_to_rule_them_all_var_arn
  s3_bucket        = var.s3bucket_lambda_code_var_id
  s3_key           = aws_s3_object.s3object_lambda_AI_AGENT_NAME_q_a.key
  handler          = "AI_AGENT_NAME_q_a.lambda_handler"
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 512
  source_code_hash = data.archive_file.archive_lambda_AI_AGENT_NAME_q_a.output_base64sha256
  environment {
    variables = {
      REGION_AWS                 = var.region_var
      OPENSEARCH_DOMAIN_ENDPOINT = var.op_domain_endpoint_var
    }
  }
  tags = merge(
    var.localTags,
    tomap({ "Name" = local.lambda_AI_AGENT_NAME_q_a_var })
  )
}

resource "aws_lambda_permission" "allow_api_gatewayAI_AGENT_NAME_q_a" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_AI_AGENT_NAME_q_a.function_name
  principal     = "apigateway.amazonaws.com"
}



