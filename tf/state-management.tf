terraform {
  backend "s3" {
    // bucket versioning is enabled
    bucket         = "tfstate-files-AI_AGENT_NAME"
    key            = "backend.tfstate"
    region         = "us-east-1"
    encrypt        = true # Encrypt the state file in S3
    // dynamodb_table partition is LockID
    dynamodb_table = "tfstate-lock-AI_AGENT_NAME"
  }
}
