output "s3bucket_raw_image_arn" {
  value = aws_s3_bucket.s3bucket_raw_image.arn
}

output "s3bucket_lambda_code_id" {
  value = aws_s3_bucket.s3bucket_lambda_code.id
}




