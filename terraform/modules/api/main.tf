data "aws_region" "current" {
}

data "aws_caller_identity" "current" {
}

resource "aws_apigatewayv2_api" "api" {
  name          = "${var.env_code}-apigw-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_authorizer" "cognito_authorizer" {
  api_id           = aws_apigatewayv2_api.api.id
  name             = "${var.env_code}-apigw-authorizer-cognito"
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  jwt_configuration {
    issuer   = var.issuer
    audience = [var.audience]
  }
}

data "aws_iam_policy_document" "assume_role_lambda" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "contacts_role" {
  name                = "${var.env_code}-iam-role-service-contacts"
  assume_role_policy  = data.aws_iam_policy_document.assume_role_lambda.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
}

data "local_file" "contacts_zip" {
  filename = "${path.module}/../../../api/contacts/dist/package.zip"
}

resource "aws_lambda_function" "contacts" {
  function_name    = "${var.env_code}-lambda-contacts"
  role             = aws_iam_role.contacts_role.arn
  filename         = data.local_file.contacts_zip.filename
  source_code_hash = data.local_file.contacts_zip.content_md5
  runtime          = "python3.11"
  handler          = "contacts.handler"
}

resource "aws_lambda_permission" "contacts_api" {
  function_name = aws_lambda_function.contacts.function_name
  action        = "lambda:InvokeFunction"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${aws_apigatewayv2_api.api.id}/*/*"
}

resource "aws_apigatewayv2_integration" "contacts" {
  api_id           = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"
  integration_uri  = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${aws_lambda_function.contacts.arn}/invocations"
}

resource "aws_apigatewayv2_route" "contacts" {
  api_id             = aws_apigatewayv2_api.api.id
  operation_name     = "Getcontacts"
  route_key          = "GET /contacts"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_authorizer.id
  target             = "integrations/${aws_apigatewayv2_integration.contacts.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}
