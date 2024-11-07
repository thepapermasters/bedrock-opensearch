// sqs queue
output "queue_metadata_pdf_arn" {
  value = aws_sqs_queue.queue_metadata_pdf.arn
}
output "queue_metadata_pdf_url" {
  value = aws_sqs_queue.queue_metadata_pdf.url
}
output "queue_metadata_pdf_name" {
  value = aws_sqs_queue.queue_metadata_pdf.name
}
output "queue_dlq_metadata_pdf_arn" {
  value = aws_sqs_queue.queue_dlq_metadata_pdf.arn
}