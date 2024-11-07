//value comes from main.tf
variable "localTags" {
  description = "Name of the project Environment State"
}

//value comes from main.tf
variable "localPrefix" {
  description = "Prefix name of the project"
}

# value comes from main.tf
variable "region_var" {
  description = "region_var"
}

# value comes from main.tf
variable "op_domain_var_arn" {
  description = "op_domain_var_arn"
}

# Names of resources
locals {
  vpc_main_var                       = "${var.localPrefix}-vpc-main"
  subnet_main_var                    = "${var.localPrefix}-subnet-main"
  subnet_main_cidr_block_var         = "11.0.1.0/24"
  security_group_main_var            = "${var.localPrefix}-security-group-AI_AGENT_NAME-dev-vpc-main"
  security_group_opensearch_main_var = "${var.localPrefix}-vpc-main-security-group-opensearch-main"
  security_group_batch_var           = "${var.localPrefix}-vpc-main-security-group-batch-main"
  vpc_endpoint_opensearch_main_var   = "${var.localPrefix}-vpc-main-endpoint-opensearch-main"
  vpc_endpoint_s3_var                = "${var.localPrefix}-vpc-main-endpoint-s3"
  vpc_endpoint_ecr_api_var           = "${var.localPrefix}-vpc-main-endpoint-ecr-api"
  vpc_endpoint_ecr_dkr_var           = "${var.localPrefix}-vpc-main-endpoint-ecr-dkr"
  vpc_endpoint_cloudwatch_var        = "${var.localPrefix}-vpc-main-endpoint-cloudwatch"
}

########
# variable "app_name" {}
# variable "availability_zones" {}
# variable "vpc_cidr_block" {}
# variable "region_name" {}