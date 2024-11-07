data "aws_iam_policy_document" "iam_policy_document_os_domain" {
  statement {
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = ["*"]
    }
    #     actions = ["es:*"]
    #     resources = ["${aws_opensearch_domain.os_domain.arn}/*"]
    actions = ["*"]
    resources = ["*"]
  }
}

resource "aws_opensearch_domain_policy" "os_domain_policy" {
  domain_name     = aws_opensearch_domain.os_domain.domain_name
  access_policies = data.aws_iam_policy_document.iam_policy_document_os_domain.json
}

resource "aws_opensearch_domain" "os_domain" {
  domain_name     = local.op_domain
  engine_version  = "OpenSearch_2.15"
  access_policies = data.aws_iam_policy_document.iam_policy_document_os_domain.json
  cluster_config {
    instance_type = "r6g.large.search"         # Hot node instance type - must use graviton instance
    instance_count = 1                        # Number of hot data nodes
    #     dedicated_master_enabled = true
    #     dedicated_master_type = "r6g.large.search"         # Master node instance type
    #     dedicated_master_count = 3                        # Number of master nodes, has to at least 3
    #     zone_awareness_enabled   = true
    #     zone_awareness_config {
    #       availability_zone_count = 3                            # Number of availability zones
    #     }
    #     warm_enabled = true                       # Enable UltraWarm storage
    #     warm_type = "ultrawarm1.medium.search" # UltraWarm instance type
    #     warm_count = 2                         # Number of UltraWarm nodes
  }
  vpc_options {
    subnet_ids = [
      var.subnet_main_id_var
    ]
    security_group_ids = [var.security_group_opensearch_main_id_var]
  }

  advanced_options = {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  # Required: EBS storage configuration
  ebs_options {
    ebs_enabled = true
    volume_type = "gp2"  # Size in GiB for hot data node storage
    volume_size = 20  # Size in GiB for hot data node storage - watch out for this - its expensive
  }
  #   encryption_at_rest {
  #   enabled = true
  # }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
  #     node_to_node_encryption {
  #     enabled = true
  #   }
  #   advanced_security_options {
  #     enabled                        = true
  #     internal_user_database_enabled = true
  #     master_user_options {
  #       master_user_name = "admin"            # Replace with your username
  #       master_user_password = "password123!"     # Replace with your password
  #     }
  #   }
  #   depends_on = [var.subnet_main_id_var]
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.op_domain
    })
  )
}



