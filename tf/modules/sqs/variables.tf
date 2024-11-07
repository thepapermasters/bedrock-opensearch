//value comes from main.tf
variable "localTags" {
  description = "Name of the project Environment State"
}

//value comes from main.tf
variable "localPrefix" {
  description = "Prefix name of the project"
}
# //value comes from main.tf
variable "lambda_AI_AGENT_NAME_mapping_var_arn" {
  description = "lambda_AI_AGENT_NAME_mapping_var_arn"
}

# Names of resources
locals {
  queue_metadata_pdf_var     = "${var.localPrefix}-metadata-pdf"
  queue_dlq_metadata_pdf_var = "${var.localPrefix}-dlq-metadata-pdf"
}

