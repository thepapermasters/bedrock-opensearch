resource "aws_iam_role" "iam_role_batch_AI_AGENT_NAME" {
  name = local.iam_role_batch_var
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : [
            "batch.amazonaws.com",
            "ecs-tasks.amazonaws.com",
            "s3.amazonaws.com",
            "dynamodb.amazonaws.com",
            "logs.amazonaws.com"
          ]
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_batch_service_1" {
  role       = aws_iam_role.iam_role_batch_AI_AGENT_NAME.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_batch_service_2" {
  role       = aws_iam_role.iam_role_batch_AI_AGENT_NAME.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_batch_service_3" {
  role       = aws_iam_role.iam_role_batch_AI_AGENT_NAME.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_batch_service_4" {
  role       = aws_iam_role.iam_role_batch_AI_AGENT_NAME.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_batch_service_5" {
  role       = aws_iam_role.iam_role_batch_AI_AGENT_NAME.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_batch_job_queue" "batch_job_queue_AI_AGENT_NAME" {
  name     = local.batch_job_queue_AI_AGENT_NAME_var
  state    = "ENABLED"
  priority = 1
  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.batch_compute_fargate_AI_AGENT_NAME.arn
  }
}


resource "aws_batch_job_definition" "batch_job_definition_AI_AGENT_NAME_config" {
  name = local.batch_job_definition_AI_AGENT_NAME_config_var
  type = "container"
  platform_capabilities = [
    "FARGATE"
  ]
  retry_strategy {
    attempts = 3  # Number of retry attempts
  }

  container_properties = jsonencode({
    container_name = local.container_name_var
    image          = "${aws_ecr_repository.ecr_repo.repository_url}:latest"
    command = ["/usr/local/bin/python3", "/app/batch/configure_os.py"]
    jobRoleArn     = aws_iam_role.iam_role_batch_AI_AGENT_NAME.arn

    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = var.cw_log_group_task_execution_batch_var_name
        awslogs-region        = var.region_var
        awslogs-stream-prefix = "batch"
      }
    },
    environment = [
      { name = "REGION_AWS", value = var.region_var },
      { name = "OPENSEARCH_DOMAIN_NAME", value = var.op_domain_var_domain_name },
      { name = "OPENSEARCH_DOMAIN_ENDPOINT", value = var.op_domain_var_endpoint },
    ]

    resourceRequirements = [
      {
        type  = "VCPU"
        value = "2"
      },
      {
        type  = "MEMORY"
        value = "16384"
      }
    ],
    executionRoleArn = aws_iam_role.iam_role_task_execution_batch.arn
  })
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.batch_job_definition_AI_AGENT_NAME_config_var
    })
  )
}


resource "aws_batch_job_definition" "batch_job_definition_AI_AGENT_NAME" {
  name = local.batch_job_definition_AI_AGENT_NAME_var
  type = "container"
  platform_capabilities = [
    "FARGATE"
  ]
  retry_strategy {
    attempts = 3  # Number of retry attempts
  }
  container_properties = jsonencode({
    container_name = local.container_name_var
    image          = "${aws_ecr_repository.ecr_repo.repository_url}:latest"
    command = ["/usr/local/bin/python3", "/app/batch/AI_AGENT_NAME_batch.py"]
    jobRoleArn     = aws_iam_role.iam_role_batch_AI_AGENT_NAME.arn
    parameters = {
      "envOverrides" = "true"
    }
    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = var.cw_log_group_task_execution_batch_var_name
        awslogs-region        = var.region_var
        awslogs-stream-prefix = "batch"
      }
    },
    environment = [
      { name = "TABLE_NAME", value = var.dynamo_tracker_var_name },
      { name = "REGION_AWS", value = var.region_var },
      { name = "OPENSEARCH_DOMAIN_NAME", value = var.op_domain_var_domain_name },
      { name = "OPENSEARCH_DOMAIN_ENDPOINT", value = var.op_domain_var_endpoint },
      { name = "S3_BUCKET_NAME_RAW_IMAGE", value = var.s3bucket_raw_image_var_arn },
      { name = "SQS_MESSAGE", value = "" }
    ]

    resourceRequirements = [
      {
        type  = "VCPU"
        value = "2"
      },
      {
        type  = "MEMORY"
        value = "16384"
      }
    ],
    executionRoleArn = aws_iam_role.iam_role_task_execution_batch.arn
  })
  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.batch_job_definition_AI_AGENT_NAME_var
    })
  )
}

resource "aws_batch_compute_environment" "batch_compute_fargate_AI_AGENT_NAME" {
  compute_environment_name = local.batch_compute_fargate_AI_AGENT_NAME_var
  compute_resources {
    max_vcpus = 64
    security_group_ids = [
      var.security_group_opensearch_main_id_var
    ]
    subnets = [
      var.subnet_main_id_var
    ]
    type = "FARGATE_SPOT"
  }
  service_role = aws_iam_role.iam_role_batch_AI_AGENT_NAME.arn
  type         = "MANAGED"

  tags = merge(
    var.localTags,
    tomap({
      "Name" = local.batch_compute_fargate_AI_AGENT_NAME_var
    })
  )
}

resource "aws_iam_role" "iam_role_pipes_batch_AI_AGENT_NAME" {
  name = local.iam_role_pipes_batch_AI_AGENT_NAME_var
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = {
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = "pipes.amazonaws.com"
      }
    }
  })
}


resource "aws_iam_role_policy" "iam_policy_pipe_sqs_to_batch" {
  role = aws_iam_role.iam_role_pipes_batch_AI_AGENT_NAME.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "batch:SubmitJob",
          "batch:DescribeJobs",
          "batch:UpdateJobQueue",
          "batch:ListJobQueues",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = [
          var.queue_metadata_pdf_var_arn,
          aws_batch_job_queue.batch_job_queue_AI_AGENT_NAME.arn,
          aws_batch_job_definition.batch_job_definition_AI_AGENT_NAME.arn
        ]
      },
    ]
  })
}

resource "aws_pipes_pipe" "pipe_sqs_to_batch_job_queue" {
  name        = local.pipe_sqs_to_batch_job_queue_var
  description = "A pipe to trigger AWS Batch jobs from SQS"
  role_arn    = aws_iam_role.iam_role_pipes_batch_AI_AGENT_NAME.arn
  source      = var.queue_metadata_pdf_var_arn
  target      = aws_batch_job_queue.batch_job_queue_AI_AGENT_NAME.arn

  # Source configuration for SQS
  source_parameters {
    sqs_queue_parameters {
      batch_size = 1
    }
  }
  # https://stackoverflow.com/questions/76299104/eventbridge-pipe-sqs-eventbus-using-sqs-message-body-as-event-detail
  # https://towardsaws.com/eventbridge-pipes-using-terraform-ae3abe6266cc
  target_parameters {
    input_template = "{ \"SQS_MESSAGE\" : <$.body> }"
    batch_job_parameters {
      job_name       = local.batch_job_name_AI_AGENT_NAME_var
      job_definition = aws_batch_job_definition.batch_job_definition_AI_AGENT_NAME.arn
      #       container_overrides {
      #         environment {
      #           name  = "SQS_MESSAGE"
      #           value = "<$.body>"
      #         }
      #       }
    }
  }
  log_configuration {
    include_execution_data = ["ALL"]
    level = "INFO"
    cloudwatch_logs_log_destination {
      log_group_arn = var.cw_log_group_task_execution_batch_var_arn
    }
  }
}


