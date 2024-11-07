module "vpc" {
  source            = "./modules/vpc"
  localTags         = local.common_tags
  localPrefix       = local.prefix
  region_var        = var.region_var
  op_domain_var_arn = module.opensearch.op_domain_arn
}

module "dynamo" {
  source      = "./modules/dynamo"
  localTags   = local.common_tags
  localPrefix = local.prefix
}

module "batch" {
  source                                     = "./modules/batch"
  localTags                                  = local.common_tags
  localPrefix                                = local.prefix
  subnet_main_id_var                         = module.vpc.subnet_main_id
  security_group_opensearch_main_id_var      = module.vpc.security_group_opensearch_main_id
  s3bucket_raw_image_var_arn                 = module.s3.s3bucket_raw_image_arn
  op_domain_var_domain_name                  = module.opensearch.os_domain_domain_name
  op_domain_var_arn                          = module.opensearch.op_domain_arn
  op_domain_var_endpoint                     = module.opensearch.op_domain_endpoint
  region_var                                 = var.region_var
  dynamo_tracker_var_name                    = module.dynamo.dynamo_tracker_name
  cw_log_group_task_execution_batch_var_name = module.cloudwatch.cw_log_group_task_execution_batch_name
  cw_log_group_task_execution_batch_var_arn  = module.cloudwatch.cw_log_group_task_execution_batch_arn
  queue_metadata_pdf_var_arn                 = module.sqs.queue_metadata_pdf_arn
}

module "s3" {
  source      = "./modules/s3"
  localTags   = local.common_tags
  localPrefix = local.prefix
}

module "sqs" {
  source                      = "./modules/sqs"
  localTags                   = local.common_tags
  localPrefix                 = local.prefix
  lambda_AI_AGENT_NAME_mapping_var_arn = module.lambda.lambda_AI_AGENT_NAME_mapping_arn
}

variable "API_AI_AGENT_NAME_MAPPING_URL" {
  description = "Description of the API_AI_AGENT_NAME_MAPPING_URL"
  type        = string
  default     = "no_url_set"  # Optional default value
}
variable "API_AI_AGENT_NAME_MAPPING_PASSWORD" {
  description = "Description of the API_AI_AGENT_NAME_MAPPING_PASSWORD"
  type        = string
  default     = "API_AI_AGENT_NAME_MAPPING_PASSWORD"
}

variable "API_AI_AGENT_NAME_MAPPING_USER" {
  description = "Description of the API_AI_AGENT_NAME_MAPPING_USER"
  type        = string
  default     = "API_AI_AGENT_NAME_MAPPING_USER"
}

module "lambda" {
  source                         = "./modules/lambda"
  localTags                      = local.common_tags
  localPrefix                    = local.prefix
  s3bucket_lambda_code_var_id    = module.s3.s3bucket_lambda_code_id
  dynamo_tracker_var_arn         = module.dynamo.dynamo_tracker_arn
  region_var                     = var.region_var
  queue_metadata_pdf_var_url     = module.sqs.queue_metadata_pdf_url
  queue_dlq_metadata_pdf_var_arn = module.sqs.queue_dlq_metadata_pdf_arn
  API_AI_AGENT_NAME_MAPPING_URL           = var.API_AI_AGENT_NAME_MAPPING_URL
  API_AI_AGENT_NAME_MAPPING_PASSWORD      = var.API_AI_AGENT_NAME_MAPPING_PASSWORD
  API_AI_AGENT_NAME_MAPPING_USER          = var.API_AI_AGENT_NAME_MAPPING_USER
  op_domain_endpoint_var         = module.opensearch.op_domain_endpoint
}

module "opensearch" {
  source                                = "./modules/opensearch"
  localTags                             = local.common_tags
  localPrefix                           = local.prefix
  vpc_main_var                          = module.vpc.vpc_main
  subnet_main_id_var                    = module.vpc.subnet_main_id
  security_group_opensearch_main_id_var = module.vpc.security_group_opensearch_main_id
}

module "cloudwatch" {
  source      = "./modules/cloudwatch"
  localTags   = local.common_tags
  localPrefix = local.prefix
}


########
# provider "aws" {
#   region = var.region_name
#   profile = "CUSTOMER"
# }
#
# locals {
#   app_name           = "aoss-qa-${var.env_suffix}"
#   opensearch_index   = "opensearch-index-${local.app_name}"
#   availability_zones = {1: "${var.region_name}a", 2: "${var.region_name}b", 3: "${var.region_name}c"}
#   vpc_cidr_block     = "10.0.0.0/22"
# }
#
# module "lambda_bedrock" {
#   source = "../../modules/lambda"
#   image_uri                  = var.bedrock_image_uri
#   app_name                   = local.app_name
#   env_name                   = var.env_suffix
#   security_group_ids         = [module.vpc.main_vpc_security_group_id]
#   subnet_ids                 = module.vpc.main_vpc_subnet_ids
#   env_vars = {
#       AOSS_URL = module.opensearch.opensearch_endpoint
#       AOSS_PORT = 443
#       INDEX_NAME = local.opensearch_index
#       BEDROCK_ENDPOINT = "https://bedrock-runtime.${var.region_name}.amazonaws.com"
#     }
#   function_name = "bedrock"
#   policy_actions = [
#     "bedrock:*",
#     "ec2:CreateNetworkInterface",
#     "ec2:DescribeNetworkInterfaces",
#     "ec2:DescribeSubnets",
#     "ec2:DeleteNetworkInterface",
#     "ec2:AssignPrivateIpAddresses",
#     "ec2:UnassignPrivateIpAddresses",
#     "ec2:DescribeSecurityGroups",
#     "ec2:DescribeSubnets",
#     "ec2:DescribeVpcs",
#   ]
# }
#
# module "lambda_opensearch" {
#   source = "../../modules/lambda"
#
#   image_uri                  = var.opensearch_image_uri
#   app_name                   = local.app_name
#   env_name                   = var.env_suffix
#   security_group_ids         = [module.vpc.main_vpc_security_group_id]
#   subnet_ids                 = module.vpc.main_vpc_subnet_ids
#   env_vars = {
#       AOSS_URL = module.opensearch.opensearch_endpoint
#       AOSS_PORT = 443
#       INDEX_NAME = local.opensearch_index
#       BEDROCK_ENDPOINT = "https://bedrock-runtime.${var.region_name}.amazonaws.com"
#       S3_BUCKET = "${local.app_name}-data-bucket"
#     }
#   function_name = "opensearch"
#   policy_actions = [
#     "bedrock:*",
#     "elasticsearch:*",
#     "s3:GetObject",
#     "ec2:CreateNetworkInterface",
#     "ec2:DescribeNetworkInterfaces",
#     "ec2:DescribeSubnets",
#     "ec2:DeleteNetworkInterface",
#     "ec2:AssignPrivateIpAddresses",
#     "ec2:UnassignPrivateIpAddresses",
#     "ec2:DescribeSecurityGroups",
#     "ec2:DescribeSubnets",
#     "ec2:DescribeVpcs",
#   ]
# }
#
# module "opensearch" {
#   source             = "../../modules/opensearch"
#   app_name           = local.app_name
#   engine_version     = "OpenSearch_2.13"
#   instance_type      = "t3.small.search"
#   instance_count     = 1
#   security_group_ids = [module.vpc.main_vpc_security_group_id]
#   subnet_ids         = module.vpc.main_vpc_subnet_ids
#   vpc_id             = module.vpc.main_vpc_id
# }
#
# module "vpc" {
#   source             = "../../modules/vpc"
#   app_name           = local.app_name
#   availability_zones = local.availability_zones
#   vpc_cidr_block     = local.vpc_cidr_block
#   region_name        = var.region_name
# }