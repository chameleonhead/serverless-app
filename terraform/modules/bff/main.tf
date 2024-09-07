data "aws_region" "current" {
}

data "aws_caller_identity" "current" {
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

resource "aws_iam_role" "auth_role" {
  name                = "${var.env_code}-iam-role-service-auth"
  assume_role_policy  = data.aws_iam_policy_document.assume_role_lambda.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
}

data "aws_iam_policy_document" "auth_role_policy" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:${var.env_code}/serverless-app/api-client-*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "cognito-idp:AdminInitiateAuth"
    ]
    resources = [
      "arn:aws:cognito-idp:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:userpool/${var.cognito_user_pool_id}"
    ]
  }
}

resource "aws_iam_role_policy" "auth_role_policy" {
  role   = aws_iam_role.auth_role.id
  policy = data.aws_iam_policy_document.auth_role_policy.json
}

data "local_file" "auth_zip" {
  filename = "${path.module}/../../../bff/auth/dist/package.zip"
}

resource "aws_lambda_function" "auth" {
  function_name    = "${var.env_code}-lambda-auth"
  role             = aws_iam_role.auth_role.arn
  filename         = data.local_file.auth_zip.filename
  source_code_hash = data.local_file.auth_zip.content_md5
  runtime          = "python3.11"
  handler          = "auth.handler"
  environment {
    variables = {
      "USER_POOL_ID"         = var.cognito_user_pool_id
      "API_CLIENT_SECRET_ID" = "${var.env_code}/serverless-app/api-client"
    }
  }
}

resource "aws_lambda_function_url" "auth_url" {
  function_name      = aws_lambda_function.auth.function_name
  authorization_type = "AWS_IAM"
}
