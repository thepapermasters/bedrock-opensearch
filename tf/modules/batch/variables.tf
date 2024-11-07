//value comes from main.tf
variable "localTags" {
  description = "Name of the project Environment State"
}

//value comes from main.tf
variable "localPrefix" {
  description = "Prefix name of the project"
}

//value comes from main.tf
variable "security_group_opensearch_main_id_var" {
  description = "security_group_opensearch_main_id_var"
}

//value comes from main.tf
variable "subnet_main_id_var" {
  description = "subnet_main_id_var"
}

# value comes from main.tf
variable "s3bucket_raw_image_var_arn" {
  description = "s3bucket_raw_image_var_arn"
}

# value comes from main.tf
variable "op_domain_var_domain_name" {
  description = "op_domain_var_domain_name"
}

# value comes from main.tf
variable "op_domain_var_endpoint" {
  description = "op_domain_var_endpoint"
}

# value comes from main.tf
variable "op_domain_var_arn" {
  description = "op_domain_var_arn"
}

# value comes from main.tf
variable "queue_metadata_pdf_var_arn" {
  description = "queue_metadata_pdf_var_arn"
}
# value comes from main.tf
variable "region_var" {
  description = "region_var"
}

# value comes from main.tf
variable "dynamo_tracker_var_name" {
  description = "dynamo_tracker_var_name"
}

# value comes from main.tf
variable "cw_log_group_task_execution_batch_var_name" {
  description = "cw_log_group_task_execution_batch_var_name"
}

# value comes from main.tf
variable "cw_log_group_task_execution_batch_var_arn" {
  description = "cw_log_group_task_execution_batch_var_arn"
}


# Names of resources
locals {
  container_name_var             = "${var.localPrefix}-container"
  ecr_repo_var                   = "${var.localPrefix}-repo"
  batch_compute_fargate_AI_AGENT_NAME_var = "${var.localPrefix}-compute-fargate"

  batch_job_name_AI_AGENT_NAME_var              = "${var.localPrefix}-job-name-AI_AGENT_NAME"
  batch_job_queue_AI_AGENT_NAME_var             = "${var.localPrefix}-job-queue-AI_AGENT_NAME"
  batch_job_definition_AI_AGENT_NAME_var        = "${var.localPrefix}-job-definition-AI_AGENT_NAME"
  batch_job_definition_AI_AGENT_NAME_config_var = "${var.localPrefix}-job-definition-AI_AGENT_NAME-config"

  pipe_sqs_to_batch_job_queue_var = "${var.localPrefix}-sqs-to-batch-job-queue"
  iam_role_pipes_batch_AI_AGENT_NAME_var   = "${var.localPrefix}-pipes-batch"
  batch_aws_service_role_var      = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"

  iam_policy_batch_var = "${var.localPrefix}-policy-batch"
  iam_role_batch_var   = "${var.localPrefix}-role-batch"

  iam_policy_host_execution_batch_var = "${var.localPrefix}-policy-host-execution-batch"
  iam_policy_task_execution_batch_var = "${var.localPrefix}-policy-task-execution-batch"
  iam_role_task_execution_batch_var   = "${var.localPrefix}-role-task-execution-batch"
  iam_role_host_execution_batch_var   = "${var.localPrefix}-role-host-execution-batch"
}
