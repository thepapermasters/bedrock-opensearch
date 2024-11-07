//value comes from main.tf
variable "localTags" {
  description = "Name of the project Environment State"
}

//value comes from main.tf
variable "localPrefix" {
  description = "Prefix name of the project"
}

// s3-lambda -- value comes from main.tf
variable "s3bucket_lambda_code_var_id" {
  description = "The s3 bucket that holds lambda code."
}

# value comes from main.tf
variable "region_var" {
  description = "region_var"
}

# value comes from main.tf
variable "op_domain_endpoint_var" {
  description = "op_domain_endpoint_var"
}


# value comes from main.tf
variable "dynamo_tracker_var_arn" {
  description = "dynamo_tracker_var_arn"
}

# value comes from main.tf
variable "queue_metadata_pdf_var_url" {
  description = "queue_metadata_pdf_var_url"
}
# value comes from main.tf
variable "queue_dlq_metadata_pdf_var_arn" {
  description = "queue_dlq_metadata_pdf_var_arn"
}

variable "API_AI_AGENT_NAME_MAPPING_URL" {
  type        = string
  description = "TF_VAR_API_AI_AGENT_NAME_MAPPING_URL"
  default     = "NOTSET"
  #   sensitive   = true  # Mark it as sensitive to hide output in Terraform logs
}

variable "API_AI_AGENT_NAME_MAPPING_USER" {
  type        = string
  description = "TF_VAR_API_AI_AGENT_NAME_MAPPING_URL"
  default     = "NOTSET"
  #   sensitive   = true  # Mark it as sensitive to hide output in Terraform logs
}

variable "API_AI_AGENT_NAME_MAPPING_PASSWORD" {
  type        = string
  description = "TF_VAR_API_AI_AGENT_NAME_MAPPING_PASSWORD"
  default     = "NOTSET"
  #   sensitive   = true  # Mark it as sensitive to hide output in Terraform logs
}

variable "API_AI_AGENT_NAME_MAPPING_URL_POST_PATH" {
  type        = string
  description = "TF_VAR_API_AI_AGENT_NAME_MAPPING_URL_POST_PATH"
  default     = "NOTSET"
  #   sensitive   = true  # Mark it as sensitive to hide output in Terraform logs
}

# Names of resources
locals {
  lambda_role_to_rule_them_all_var     = "${var.localPrefix}-lambda-role-to-rule-them-all"
  lambda_role_to_rule_them_all_var_arn = aws_iam_role.lambda_role_to_rule_them_all.arn
  lambda_user_authorizer_var           = "${var.localPrefix}-user-authorizer"
  lambda_AI_AGENT_NAME_mapping_var              = "${var.localPrefix}-AI_AGENT_NAME-mapping"
  lambda_AI_AGENT_NAME_q_a_var                  = "${var.localPrefix}-AI_AGENT_NAME-q-a"
}


# variable "image_uri" {}
# variable "subnet_ids" {}
# variable "security_group_ids" {}
# variable "app_name" {}
# variable "env_name" {}
# variable "env_vars" {}
# variable "function_name" {}
# variable "policy_actions" {}