# S3 bucket where images are stored
resource "aws_s3_bucket" "s3bucket_raw_image" {
  bucket = local.s3bucket_raw_image_var
  tags = merge(
    var.localTags,
    tomap({ "Name" = local.s3bucket_raw_image_var })
  )
}


