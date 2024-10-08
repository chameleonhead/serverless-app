data "aws_caller_identity" "current" {
}

data "aws_region" "current" {
}

resource "aws_s3_bucket" "frontend_assets" {
  bucket = "${var.env_code}-s3-frontend-assets-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "frontend_assets_pab" {
  bucket = aws_s3_bucket.frontend_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "frontend_assets_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.frontend_assets.arn,
      "${aws_s3_bucket.frontend_assets.arn}/*"
    ]
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = ["arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/${aws_cloudfront_distribution.frontend.id}"]
    }
  }
}

resource "aws_s3_bucket_policy" "frontend_assets_policy" {
  bucket = aws_s3_bucket.frontend_assets.bucket
  policy = data.aws_iam_policy_document.frontend_assets_policy.json
}

resource "aws_cloudfront_origin_access_control" "s3" {
  name                              = "${var.env_code}-serverless-app-s3"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_origin_access_control" "lambda" {
  name                              = "${var.env_code}-serverless-app-lambda"
  origin_access_control_origin_type = "lambda"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "frontend" {
  origin {
    origin_id                = "origin-s3"
    domain_name              = aws_s3_bucket.frontend_assets.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.s3.id
  }

  origin {
    origin_id                = "origin-auth"
    domain_name              = var.bff_auth_url_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.lambda.id

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }

    origin_shield {
      enabled              = true
      origin_shield_region = data.aws_region.current.name
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  custom_error_response {
    error_code            = 404
    error_caching_min_ttl = 300
    response_code         = 200
    response_page_path    = "/index.html"
  }

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "origin-s3"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  ordered_cache_behavior {
    path_pattern     = "/auth/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "origin-auth"

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad" // Managed-CachingDisabled
    origin_request_policy_id = "b689b0a8-53d0-40ab-baf2-68738e2966ac" // Managed-AllViewerExceptHostHeader

    viewer_protocol_policy = "allow-all"
    default_ttl            = 0
    min_ttl                = 0
    max_ttl                = 0
    smooth_streaming       = false
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
      locations        = []
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

locals {
  content_type_map = {
    "html" = "text/html"
    "css"  = "text/css"
    "js"   = "text/javascript"
    "svg"  = "image/svg+xml"
  }
}

data "local_file" "dist" {
  for_each = toset([for s in fileset("${path.module}/../../../frontend/dist", "**") : s])
  filename = "${path.module}/../../../frontend/dist/${each.value}"
}

resource "aws_s3_object" "dist" {
  for_each      = toset([for i in data.local_file.dist : i.filename])
  bucket        = aws_s3_bucket.frontend_assets.bucket
  key           = replace(each.value, "${path.module}/../../../frontend/dist/", "")
  source        = each.value
  etag          = filemd5(each.value)
  content_type  = lookup(local.content_type_map, element(split(".", each.value), length(split(".", each.value)) - 1), "application/octet-stream")
  cache_control = element(split("/", each.value), length(split("/", each.value)) - 1) == "index.html" ? "no-cache" : null
}

resource "aws_cognito_user_pool_client" "api_client" {
  user_pool_id    = var.user_pool_id
  name            = "${var.env_code}-cognito-client-api"
  generate_secret = true
  callback_urls = [
    "https://${aws_cloudfront_distribution.frontend.domain_name}/auth/callback"
  ]
  default_redirect_uri                 = "https://${aws_cloudfront_distribution.frontend.domain_name}/auth/callback"
  explicit_auth_flows                  = ["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "profile", "email"]
  supported_identity_providers         = ["COGNITO"]
}

resource "aws_secretsmanager_secret" "api_client" {
  name = "${var.env_code}/serverless-app/api-client"
}

resource "aws_secretsmanager_secret_version" "api_client_main" {
  secret_id = aws_secretsmanager_secret.api_client.id
  secret_string = jsonencode({
    "client_id"     = aws_cognito_user_pool_client.api_client.id,
    "client_secret" = aws_cognito_user_pool_client.api_client.client_secret,
    "redirect_uri"  = "https://${aws_cloudfront_distribution.frontend.domain_name}/auth/callback"
  })
}

resource "aws_lambda_permission" "auth_api" {
  function_name = var.bff_auth_function_name
  action        = "lambda:InvokeFunctionUrl"
  principal     = "cloudfront.amazonaws.com"
  source_arn    = "arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/${aws_cloudfront_distribution.frontend.id}"
}
