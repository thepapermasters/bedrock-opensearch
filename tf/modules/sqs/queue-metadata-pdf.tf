resource "aws_sqs_queue_policy" "queue_metadata_pdf_policy" {
  queue_url = aws_sqs_queue.queue_metadata_pdf.url
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:*"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Principal = {
          Service = "sqs.amazonaws.com"
        },
        Action = [
          "sqs:*"
        ],
        Resource = aws_sqs_queue.queue_metadata_pdf.arn,
      }
    ]
  })
}

resource "aws_sqs_queue" "queue_metadata_pdf" {
  name             = local.queue_metadata_pdf_var
  fifo_queue       = false
  max_message_size = 262144
  tags = merge(
    var.localTags,
    tomap({ "Name" = local.queue_metadata_pdf_var })
  )
}

resource "aws_sqs_queue" "queue_dlq_metadata_pdf" {
  name                      = local.queue_dlq_metadata_pdf_var
  message_retention_seconds = 1209600
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns = [aws_sqs_queue.queue_metadata_pdf.arn]
  })
  tags = merge(
    var.localTags,
    tomap({ "Name" = local.queue_dlq_metadata_pdf_var })
  )
}

resource "aws_sqs_queue_redrive_policy" "queue_metadata_pdf_redrive_policy" {
  queue_url = aws_sqs_queue.queue_metadata_pdf.url
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.queue_dlq_metadata_pdf.arn
    maxReceiveCount     = 3
  })
}

# resource "aws_cloudwatch_metric_alarm" "cw_alarm_dlq_metadata_pdf" {
#   alarm_name          = "DLQMessageCountAlarm"
#   comparison_operator = "GreaterThanThreshold"
#   evaluation_periods  = 1
#   metric_name         = "ApproximateNumberOfMessagesVisible"
#   namespace           = "AWS/SQS"
#   period              = 60
#   statistic           = "Sum"
#   threshold           = 1
#   alarm_actions = [var.sns_topic_metadata_pdf_var_arn]
#   dimensions = {
#     QueueName = aws_sqs_queue.queue_dlq_metadata_pdf.name
#   }
# }

