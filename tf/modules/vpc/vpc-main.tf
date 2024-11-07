data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "vpc_main" {
  cidr_block           = "11.0.0.0/16"
  instance_tenancy     = "default"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.vpc_main_var
    })
  )
}

resource "aws_subnet" "subnet_main" {
  vpc_id            = aws_vpc.vpc_main.id
  cidr_block = local.subnet_main_cidr_block_var # Subnet CIDR should be a subset of the VPC CIDR
  availability_zone = data.aws_availability_zones.available.names[0]
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.subnet_main_var,
      "Tier" = "private"
    })
  )
}

resource "aws_security_group" "security_group_main" {
  name        = local.security_group_main_var
  description = "Security Group for Project"
  vpc_id      = aws_vpc.vpc_main.id
  ingress {
    description = "From anywhere inside VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.subnet_main.cidr_block] # Allow only within the subnet
  }
  egress {
    description = "To anywhere"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.security_group_main_var,
      "Tier" = "private"
    })
  )
}

resource "aws_security_group" "security_group_opensearch_main" {
  name        = local.security_group_opensearch_main_var
  description = "Security Group for Project"
  vpc_id      = aws_vpc.vpc_main.id
  ingress {
    description = "From anywhere inside VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.subnet_main.cidr_block]  # Allow only within the subnet
  }
  egress {
    description = "To anywhere"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.security_group_opensearch_main_var,
      "Tier" = "private"
    })
  )
}

resource "aws_security_group" "security_group_batch" {
  name        = local.security_group_batch_var
  description = "Security Group for Project"
  vpc_id      = aws_vpc.vpc_main.id
  ingress {
    description = "From anywhere inside VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.subnet_main.cidr_block]  # Allow only within the subnet
  }
  egress {
    description = "To anywhere"
    from_port   = 0
    to_port     = 0
    protocol = "-1" # semantically equivalent to all ports
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.security_group_batch_var,
      "Tier" = "private"
    })
  )
}

# These endpoints are needed to connect with AWS services
resource "aws_vpc_endpoint" "vpc_endpoint_s3" {
  vpc_id            = aws_vpc.vpc_main.id
  service_name      = "com.amazonaws.${var.region_var}.s3"
  route_table_ids = [aws_vpc.vpc_main.default_route_table_id]
  vpc_endpoint_type = "Gateway"
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.vpc_endpoint_s3_var,
      "Tier" = "private"
    })
  )
}

resource "aws_vpc_endpoint" "vpc_endpoint_cloudwatch" {
  service_name        = "com.amazonaws.${var.region_var}.logs"
  vpc_id              = aws_vpc.vpc_main.id
  private_dns_enabled = true
  security_group_ids = [aws_security_group.security_group_main.id]
  vpc_endpoint_type   = "Interface"
  subnet_ids = [aws_subnet.subnet_main.id]
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.vpc_endpoint_cloudwatch_var,
      "Tier" = "private"
    })
  )
}

resource "aws_vpc_endpoint" "vpc_endpoint_ecr_api" {
  service_name        = "com.amazonaws.${var.region_var}.ecr.api"
  vpc_id              = aws_vpc.vpc_main.id
  private_dns_enabled = true
  security_group_ids = [aws_security_group.security_group_main.id]
  vpc_endpoint_type   = "Interface"
  subnet_ids = [aws_subnet.subnet_main.id]
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AllowAll",
        "Effect" : "Allow",
        "Principal" : "*",
        "Action" : "*",
        "Resource" : "*"
      },
      {
        "Sid" : "PreventDelete",
        "Effect" : "Deny",
        "Principal" : "*",
        "Action" : "ecr:DeleteRepository",
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Principal" : "*", # Allow access to all principals (You can restrict this as needed)
        "Action" : [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetAuthorizationToken"
        ],
        "Resource" : [
          "*"
        ]
      }
    ]
  })
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.vpc_endpoint_ecr_api_var,
      "Tier" = "private"
    })
  )
}

resource "aws_vpc_endpoint" "vpc_endpoint_ecr_dkr" {
  service_name        = "com.amazonaws.${var.region_var}.ecr.dkr"
  vpc_id              = aws_vpc.vpc_main.id
  private_dns_enabled = true
  security_group_ids = [aws_security_group.security_group_main.id]
  vpc_endpoint_type   = "Interface"
  subnet_ids = [aws_subnet.subnet_main.id]
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : "*", # Allow access to all principals (You can restrict this as needed)
        "Action" : [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetAuthorizationToken"
        ],
        "Resource" : [
          "*"
        ]
      }
    ]
  })
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.vpc_endpoint_ecr_dkr_var,
      "Tier" = "private"
    })
  )
}

resource "aws_opensearch_vpc_endpoint" "vpc_endpoint_opensearch_main" {
  domain_arn = var.op_domain_var_arn
  vpc_options {
    security_group_ids = [aws_security_group.security_group_opensearch_main.id]
    subnet_ids = [aws_subnet.subnet_main.id]
  }
}

resource "aws_vpc_endpoint" "vpc_endpoint_batch" {
  vpc_id = aws_vpc.vpc_main.id  # Reference your VPC ID
  service_name = "com.amazonaws.${var.region_var}.batch"  # Service name for AWS Batch
  vpc_endpoint_type = "Interface"  # Interface VPC endpoint for AWS Batch
  subnet_ids = [aws_subnet.subnet_main.id] # Subnet IDs for the endpoint
  security_group_ids = [aws_security_group.security_group_batch.id]  # Security group attached to the endpoint
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.security_group_batch_var,
      "Tier" = "private"
    })
  )
}