output "serverless_app_audience" {
  value = aws_cognito_user_pool_client.api_client.id
}

output "cloudfront_endpoint" {
  value = aws_cloudfront_distribution.frontend.domain_name
}
