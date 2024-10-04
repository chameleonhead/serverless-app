data "aws_region" "current" {
}

data "aws_caller_identity" "current" {
}

resource "aws_s3_bucket" "session_storage" {
  bucket = "${var.env_code}-s3-session-storage-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "session_storage_pab" {
  bucket = aws_s3_bucket.session_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
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
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
      "s3:AbortMultipartUpload"
    ]
    resources = [
      aws_s3_bucket.session_storage.arn,
      "${aws_s3_bucket.session_storage.arn}/*"
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
  timeout          = 59
  environment {
    variables = {
      "S3_BUCKET"                = aws_s3_bucket.session_storage.bucket
      "COGNITO_USER_POOL_ID"     = var.cognito_user_pool_id
      "COGNITO_USER_POOL_DOMAIN" = var.cognito_user_pool_domain
      "API_CLIENT_SECRET_ID"     = "${var.env_code}/serverless-app/api-client"
    }
  }
}

resource "aws_lambda_function_url" "auth_url" {
  function_name      = aws_lambda_function.auth.function_name
  authorization_type = "AWS_IAM"
}
