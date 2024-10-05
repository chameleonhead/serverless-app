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
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "contacts_policy" {
  statement {
    effect = "Allow"
    actions = [
      "rds-db:connect"
    ]
    resources = [
      "arn:aws:rds-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dbuser:${var.db_resource_id}/contacts_api"
    ]
  }
}

resource "aws_iam_role" "contacts_role" {
  name                = "${var.env_code}-iam-role-service-contacts"
  assume_role_policy  = data.aws_iam_policy_document.assume_role_lambda.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
}

resource "aws_iam_role_policy" "contacts_policy" {
  role   = aws_iam_role.contacts_role.id
  policy = data.aws_iam_policy_document.contacts_policy.json
}

data "local_file" "contacts_zip" {
  filename = "${path.module}/../../../api/contacts/dist/package.zip"
}

resource "aws_security_group" "contacts" {
  name   = "${var.env_code}-sg-contacts"
  vpc_id = var.vpc_id
  tags = {
    Name = "${var.env_code}-sg-contacts"
  }
}

resource "aws_security_group_rule" "contacts" {
  security_group_id        = aws_security_group.contacts.id
  type                     = "egress"
  source_security_group_id = var.db_security_group_id
  protocol                 = "tcp"
  from_port                = 5432
  to_port                  = 5432
}

resource "aws_security_group_rule" "db_from_contacts" {
  security_group_id        = var.db_security_group_id
  type                     = "ingress"
  source_security_group_id = aws_security_group.contacts.id
  protocol                 = "tcp"
  from_port                = 5432
  to_port                  = 5432
}

resource "aws_lambda_function" "contacts" {
  function_name    = "${var.env_code}-lambda-contacts"
  role             = aws_iam_role.contacts_role.arn
  filename         = data.local_file.contacts_zip.filename
  source_code_hash = data.local_file.contacts_zip.content_md5
  runtime          = "python3.11"
  handler          = "contacts.handler"
  environment {
    variables = {
      DB_HOST = var.db_host
    }
  }
  vpc_config {
    subnet_ids = var.lambda_subnet_ids
    security_group_ids = [
      aws_security_group.contacts.id
    ]
  }
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
