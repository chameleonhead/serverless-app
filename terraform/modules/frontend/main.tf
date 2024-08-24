data "aws_caller_identity" "current" {
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
    actions = ["s3:GetObject"]
    resources = [
      aws_s3_bucket.frontend_assets.arn,
      "${aws_s3_bucket.frontend_assets.arn}/*"
    ]
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = ["arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/${aws_cloudfront_distribution.s3_distribution.id}"]
    }
  }
}

resource "aws_s3_bucket_policy" "frontend_assets_policy" {
  bucket = aws_s3_bucket.frontend_assets.bucket
  policy = data.aws_iam_policy_document.frontend_assets_policy.json
}

resource "aws_cloudfront_origin_access_control" "default" {
  name                              = "default"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    origin_id                = "s3origin"
    domain_name              = aws_s3_bucket.frontend_assets.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.default.id
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3origin"

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

  restrictions {
    geo_restriction {
      restriction_type = "none"
      locations        = []
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  provisioner "local-exec" {
    command = "aws cloudfront create-invalidation --distribution-id ${self.id}"
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

resource "aws_s3_object" "dist" {
  for_each = toset([for s in fileset("../frontend/dist", "**/*") : s if s != "index.html"])

  bucket       = aws_s3_bucket.frontend_assets.bucket
  key          = each.value
  source       = "../frontend/dist/${each.value}"
  etag         = filemd5("../frontend/dist/${each.value}")
  content_type = lookup(local.content_type_map, split(".", each.value)[1], "application/octet-stream")
}


resource "aws_s3_object" "dist_index" {
  bucket        = aws_s3_bucket.frontend_assets.bucket
  key           = "index.html"
  source        = "../frontend/dist/index.html"
  etag          = filemd5("../frontend/dist/index.html")
  content_type  = "text/html"
  cache_control = "no-cache"
}


