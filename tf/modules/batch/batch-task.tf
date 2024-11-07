resource "aws_iam_role" "iam_role_host_execution_batch" {
  name = local.iam_role_host_execution_batch_var
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : [
            "batch.amazonaws.com",
            "ecs-tasks.amazonaws.com",
            "logs.amazonaws.com"
          ]
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_host_execution_batch_1" {
  role       = aws_iam_role.iam_role_host_execution_batch.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_host_execution_batch_2" {
  role       = aws_iam_role.iam_role_host_execution_batch.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_host_execution_batch_3" {
  role       = aws_iam_role.iam_role_host_execution_batch.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_host_execution_batch_4" {
  role       = aws_iam_role.iam_role_host_execution_batch.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess"
}

resource "aws_iam_role" "iam_role_task_execution_batch" {
  name = local.iam_role_task_execution_batch_var
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : [
            "batch.amazonaws.com",
            "ecs-tasks.amazonaws.com",
            "logs.amazonaws.com"
          ]
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "iam_policy_task_execution_batch" {
  role = aws_iam_role.iam_role_task_execution_batch.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "dynamodb:PutItem",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_task_execution_batch_1" {
  role       = aws_iam_role.iam_role_task_execution_batch.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_task_execution_batch_2" {
  role       = aws_iam_role.iam_role_task_execution_batch.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_task_execution_batch_3" {
  role       = aws_iam_role.iam_role_task_execution_batch.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "iam_policy_attachment_task_execution_batch_4" {
  role       = aws_iam_role.iam_role_task_execution_batch.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess"
}

