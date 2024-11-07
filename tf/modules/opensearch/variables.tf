//value comes from main.tf
variable "localTags" {
  description = "Name of the project Environment State"
}

//value comes from main.tf
variable "localPrefix" {
  description = "Prefix name of the project"
}

//value comes from main.tf
variable "vpc_main_var" {
  description = "vpc_main_var"
}

//value comes from main.tf
variable "subnet_main_id_var" {
  description = "subnet_main_id_var"
}

//value comes from main.tf
variable "security_group_opensearch_main_id_var" {
  description = "security_group_opensearch_main_id_var"
}

# Names of resources
locals {
  op_domain = "${var.localPrefix}-domain"
}

#########
# variable "app_name" {}
# variable "instance_type" {}
# variable "engine_version" {}
# variable "instance_count" {}
# variable "subnet_ids" {}
# variable "vpc_id" {}
# variable "security_group_ids" {}

