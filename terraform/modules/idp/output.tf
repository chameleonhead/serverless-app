output "user_pool_id" {
  value = aws_cognito_user_pool.userpool.id
}

output "issuer" {
  value = "https://cognito-idp.${data.aws_region.current.name}.amazonaws.com/${aws_cognito_user_pool.userpool.id}"
}
