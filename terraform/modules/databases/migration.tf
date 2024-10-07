data "aws_caller_identity" "current" {
}

resource "aws_s3_bucket" "migartion_source" {
  bucket = "${var.env_code}-s3-migration-source-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "migartion_source_pab" {
  bucket = aws_s3_bucket.migartion_source.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "assume_role_codebuild" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "codebuild_migration" {
  name                = "${var.env_code}-iam-role-service-codebuild-migration"
  assume_role_policy  = data.aws_iam_policy_document.assume_role_codebuild.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/AdministratorAccess"]
}

data "local_file" "api_source_files" {
  for_each = toset([for s in fileset("${path.module}/../../../api/contacts", "**") : s if !startswith(s, ".") && !startswith(s, "dist") && !startswith(s, "contacts") && !startswith(s, "tests") && !endswith(s, ".xml") && !strcontains(s, "__pycache__")])
  filename = "${path.module}/../../../api/contacts/${each.value}"
}

data "archive_file" "api_source" {
  type        = "zip"
  output_path = "${path.module}/temp/apidb.zip"
  dynamic "source" {
    for_each = data.local_file.api_source_files
    content {
      filename = replace(source.value["filename"], "${path.module}/../../../api/contacts/", "")
      content  = source.value["content"]
    }
  }
}

resource "aws_s3_object" "api_source" {
  bucket = aws_s3_bucket.migartion_source.bucket
  key    = "apidb.zip"
  source = data.archive_file.api_source.output_path
  etag   = data.archive_file.api_source.output_md5
}

resource "aws_security_group" "cicd" {
  name   = "${var.env_code}-sg-cicd"
  vpc_id = var.vpc_id
  tags = {
    Name = "${var.env_code}-sg-cicd"
  }
}

resource "aws_security_group_rule" "apidb_from_cicd" {
  security_group_id        = aws_security_group.apidb.id
  type                     = "ingress"
  source_security_group_id = aws_security_group.cicd.id
  protocol                 = "tcp"
  from_port                = 5432
  to_port                  = 5432
}

resource "aws_security_group_rule" "cicd_to_apidb" {
  security_group_id        = aws_security_group.cicd.id
  type                     = "egress"
  source_security_group_id = aws_security_group.apidb.id
  protocol                 = "tcp"
  from_port                = 5432
  to_port                  = 5432
}

resource "aws_security_group_rule" "cicd_to_internet" {
  security_group_id = aws_security_group.cicd.id
  type              = "egress"
  cidr_blocks       = ["0.0.0.0/0"]
  protocol          = "tcp"
  from_port         = 443
  to_port           = 443
}

// CodeBuild Project
resource "aws_codebuild_project" "apidbmigration" {
  name         = "${var.env_code}-serverless-app-apidb-migration"
  service_role = aws_iam_role.codebuild_migration.arn

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = "true"

    environment_variable {
      name  = "DB_HOST"
      value = aws_rds_cluster.apidb.endpoint
    }

    environment_variable {
      name  = "DB_PORT"
      value = aws_rds_cluster.apidb.port
    }

    environment_variable {
      name  = "DB_NAME"
      value = aws_rds_cluster.apidb.database_name
    }

    environment_variable {
      name  = "DB_USER"
      value = "postgres"
    }

    environment_variable {
      name  = "DB_PASSWORD_JSON"
      type  = "SECRETS_MANAGER"
      value = aws_rds_cluster.apidb.master_user_secret[0].secret_arn
    }
  }

  source {
    type      = "S3"
    buildspec = file("${path.module}/buildspec-apidb.yml")
    location  = "${aws_s3_object.api_source.bucket}/${aws_s3_object.api_source.key}"
  }

  artifacts {
    type = "NO_ARTIFACTS"
  }

  vpc_config {
    vpc_id = var.vpc_id

    subnets = var.cicd_subnet_ids

    security_group_ids = [
      aws_security_group.cicd.id
    ]
  }
}
