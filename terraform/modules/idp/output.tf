output "user_pool_id" {
  value = aws_cognito_user_pool.userpool.id
}

output "user_pool_domain" {
  value = "${aws_cognito_user_pool_domain.userpool_domain.domain}.auth.${data.aws_region.current.name}.amazoncognito.com"
}

output "issuer" {
  value = "https://cognito-idp.${data.aws_region.current.name}.amazonaws.com/${aws_cognito_user_pool.userpool.id}"
}
