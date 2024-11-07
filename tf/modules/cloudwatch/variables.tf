//value comes from main.tf
variable "localTags" {
  description = "Name of the project Environment State"
}

//value comes from main.tf
variable "localPrefix" {
  description = "Prefix name of the project"
}
//value comes from main.tf

# Names of resources
locals {
  cw_log_group_task_execution_batch_var = "${var.localPrefix}-group-task-execution-batch"
}