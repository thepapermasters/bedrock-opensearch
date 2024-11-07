variable "region_var" {
  type    = string
  default = "us-east-1"
}

variable "project_var" {
  type    = string
  default = "AI_AGENT_NAME"
}

variable "creator_var" {
  type    = string
  default = "DEV_TEAM"
}

variable "customer_var" {
  type    = string
  default = "CUSTOMER"
}

variable "environment" {
  description = "The environment in which the resources are deployed (e.g., dev, stage, prod)."
  type        = string
}

locals {
  prefix = "${var.project_var}-${terraform.workspace}"
  region = var.region_var
  common_tags = {
    Environment = terraform.workspace
    Project     = var.project_var
    Creator     = var.creator_var
    Customer    = var.customer_var
  }
}