resource "aws_cloudwatch_log_group" "cw_log_group_task_execution_batch" {
  name              = local.cw_log_group_task_execution_batch_var
  retention_in_days = 30
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.cw_log_group_task_execution_batch_var
    })
  )
}



