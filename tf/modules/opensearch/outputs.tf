output "os_domain_domain_name" {
  value = aws_opensearch_domain.os_domain.domain_name
}

output "op_domain_id" {
  value = aws_opensearch_domain.os_domain.id
}

output "op_domain_arn" {
  value = aws_opensearch_domain.os_domain.arn
}


output "op_domain_endpoint" {
  value = aws_opensearch_domain.os_domain.endpoint
}

##########
# output "opensearch_endpoint" {
#   value = aws_opensearch_domain.opensearch-domain.endpoint
# }
# output "aws_opensearch_vpc_endpoint" {
#   value = aws_opensearch_vpc_endpoint.opensearch-endpoint.endpoint
# }