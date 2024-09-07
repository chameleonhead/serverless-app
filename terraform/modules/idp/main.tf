data "aws_region" "current" {
}

resource "aws_cognito_user_pool" "userpool" {
  name = "${var.env_code}-cognito-identity"
}

resource "aws_cognito_user_pool_domain" "userpool_domain" {
  user_pool_id = aws_cognito_user_pool.userpool.id
  domain       = "${var.env_code}-severless-app"
}

resource "aws_cognito_user" "initial_user1" {
  user_pool_id = aws_cognito_user_pool.userpool.id
  username     = "admin@example.com"
  attributes = {
    "email"          = "admin@example.com"
    "email_verified" = "true"
  }
  password = "P@ssw0rd"
}
