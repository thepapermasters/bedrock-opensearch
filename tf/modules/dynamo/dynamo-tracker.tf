resource "aws_dynamodb_table" "dynamo_tracker" {
  name             = local.dynamo_tracker_var
  billing_mode     = "PAY_PER_REQUEST"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  hash_key         = "BUCKET_KEY"

  point_in_time_recovery {
    enabled = true
  }

  attribute {
    name = "BUCKET_KEY"
    type = "S"
  }
  attribute {
    name = "STATUS"
    type = "S"
  }
  attribute {
    name = "FOLDER_ID"
    type = "N"
  }

  global_secondary_index {
    name            = "STATUS_index"
    hash_key        = "STATUS"
    projection_type = "ALL"
  }
  global_secondary_index {
    name            = "FOLDER_ID_index"
    hash_key        = "FOLDER_ID"
    projection_type = "ALL"
  }

  tags = merge(
    var.localTags,
    tomap({ "Name" = local.dynamo_tracker_var })
  )
}