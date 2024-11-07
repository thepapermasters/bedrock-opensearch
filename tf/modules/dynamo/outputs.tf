output "dynamo_tracker_arn" {
  value = aws_dynamodb_table.dynamo_tracker.arn
}

output "dynamo_tracker_name" {
  value = aws_dynamodb_table.dynamo_tracker.name
}
