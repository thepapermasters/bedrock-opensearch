//value comes from main.tf
variable "localTags" {
  description = "Name of the project Environment State"
}

//value comes from main.tf
variable "localPrefix" {
  description = "Prefix name of the project"
}

# Names of resources
locals {
  s3bucket_raw_image_var   = "${var.localPrefix}-raw-images"
  s3bucket_lambda_code_var = "${var.localPrefix}-lambda-codes"
}
