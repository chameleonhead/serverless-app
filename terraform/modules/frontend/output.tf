output "cloudfront_endpoint" {
  value = aws_cloudfront_distribution.distribution.domain_name
}
