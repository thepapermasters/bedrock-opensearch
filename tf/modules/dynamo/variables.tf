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
  dynamo_tracker_var = "${var.localPrefix}-tracker"
}

