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

resource "aws_lambda_function" "auth" {
  function_name    = "${var.env_code}-lambda-auth"
  role             = aws_iam_role.auth_role.arn
  filename         = "../bff/auth/dist/package.zip"
  source_code_hash = filesha1("../bff/auth/dist/package.zip")
  runtime          = "python3.11"
  handler          = "auth.handler"
}

resource "aws_lambda_function_url" "auth_url" {
  function_name      = aws_lambda_function.auth.function_name
  authorization_type = "AWS_IAM"
}

resource "aws_lambda_permission" "auth_api" {
  function_name = aws_lambda_function.auth.function_name
  action        = "lambda:InvokeFunctionUrl"
  principal     = "cloudfront.amazonaws.com"
  source_arn    = "arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/*"
}
