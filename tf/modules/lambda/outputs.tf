# Lambdas
output "lambda_AI_AGENT_NAME_mapping_function_name" {
  value = aws_lambda_function.lambda_AI_AGENT_NAME_mapping.function_name
}

output "lambda_AI_AGENT_NAME_mapping_arn" {
  value = aws_lambda_function.lambda_AI_AGENT_NAME_mapping.arn
}

output "lambda_AI_AGENT_NAME_q_a_function_name" {
  value = aws_lambda_function.lambda_AI_AGENT_NAME_q_a.function_name
}

output "lambda_AI_AGENT_NAME_q_a_arn" {
  value = aws_lambda_function.lambda_AI_AGENT_NAME_q_a.arn
}

###########
# output "lambda_role_arn" {
#   value = aws_iam_role.lambda_role.arn
# }
# output "arn" {
#   value = aws_lambda_function.lambda_function.arn
# }
# output "name" {
#   value = aws_lambda_function.lambda_function.function_name
# }