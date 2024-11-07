# S3 where lambda code is stored
resource "aws_s3_bucket" "s3bucket_lambda_code" {
  bucket = local.s3bucket_lambda_code_var
  tags = merge(
    var.localTags,
    tomap({ "Name" = local.s3bucket_lambda_code_var })
  )
}



