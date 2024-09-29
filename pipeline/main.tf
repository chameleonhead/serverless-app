data "aws_caller_identity" "current" {
}


// S3 Bucket for Artifact
resource "aws_s3_bucket" "artifact_bucket" {
  bucket = "${var.env_code}-s3-pipeline-bucket-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "artifact_bucket_pab" {
  bucket = aws_s3_bucket.artifact_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


// S3 Bucket for cache
resource "aws_s3_bucket" "cache_bucket" {
  bucket = "${var.env_code}-s3-cache-bucket-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "cache_bucket_pab" {
  bucket = aws_s3_bucket.cache_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

// S3 Bucket for Terraform states
resource "aws_s3_bucket" "tfstate_bucket" {
  bucket = "${var.env_code}-s3-tfstate-bucket-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "tfstate_bucket_pab" {
  bucket = aws_s3_bucket.tfstate_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

// CodeBuild Project
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

resource "aws_iam_role" "codebuild_role" {
  name                = "${var.env_code}-iam-role-service-codebuild"
  assume_role_policy  = data.aws_iam_policy_document.assume_role_codebuild.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/AdministratorAccess"]
}

resource "aws_codebuild_project" "serverless_app_build" {
  name         = "${var.env_code}-serverless-app-build"
  service_role = aws_iam_role.codebuild_role.arn

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = "true"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-build.yml"
  }

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type     = "S3"
    location = "${aws_s3_bucket.cache_bucket.bucket}/serverless-app-build"
  }
}

resource "aws_codebuild_project" "serverless_app_test" {
  name         = "${var.env_code}-serverless-app-test"
  service_role = aws_iam_role.codebuild_role.arn

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = "true"

    environment_variable {
      name  = "S3_BUCKET_TFSTATE"
      value = aws_s3_bucket.tfstate_bucket.bucket
    }

    environment_variable {
      name  = "S3_KEY_TFSTATE"
      value = "serverless-app/terraform.tfstate"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-test.yml"
  }

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type     = "S3"
    location = "${aws_s3_bucket.cache_bucket.bucket}/serverless-app-test"
  }
}

// CodePipeline Pipeline
resource "aws_codepipeline" "pipeline" {
  name           = "${var.env_code}-pipeline"
  pipeline_type  = "V2"
  execution_mode = "QUEUED"
  role_arn       = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.artifact_bucket.bucket
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn        = aws_codestarconnections_connection.serverless_app_connection.arn
        FullRepositoryId     = "chameleonhead/serverless-app"
        BranchName           = "main"
        OutputArtifactFormat = "CODEBUILD_CLONE_REF"
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "Build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.serverless_app_build.name
      }
    }
  }

  stage {
    name = "Test"

    action {
      name            = "Test"
      category        = "Test"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["build_output"]
      version         = "1"

      configuration = {
        ProjectName = aws_codebuild_project.serverless_app_test.name
      }
    }
  }

  # stage {
  #   name = "Deploy"

  #   action {
  #     name            = "Deploy"
  #     category        = "Deploy"
  #     owner           = "AWS"
  #     provider        = "CloudFormation"
  #     input_artifacts = ["build_output"]
  #     version         = "1"

  #     configuration = {
  #       ActionMode     = "REPLACE_ON_FAILURE"
  #       Capabilities   = "CAPABILITY_AUTO_EXPAND,CAPABILITY_IAM"
  #       OutputFileName = "CreateStackOutput.json"
  #       StackName      = "MyStack"
  #       TemplatePath   = "build_output::sam-templated.yaml"
  #     }
  #   }
  # }
}

resource "aws_codestarconnections_connection" "serverless_app_connection" {
  name          = "${var.env_code}-serverless-app-connection"
  provider_type = "GitHub"
}

data "aws_iam_policy_document" "assume_role_codepipeline" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["codepipeline.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "codepipeline_role" {
  name               = "${var.env_code}-iam-role-service-codepipeline"
  assume_role_policy = data.aws_iam_policy_document.assume_role_codepipeline.json
}

data "aws_iam_policy_document" "codepipeline_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketVersioning",
      "s3:PutObjectAcl",
      "s3:PutObject",
    ]

    resources = [
      aws_s3_bucket.artifact_bucket.arn,
      "${aws_s3_bucket.artifact_bucket.arn}/*"
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["codestar-connections:UseConnection"]
    resources = [aws_codestarconnections_connection.serverless_app_connection.arn]
  }

  statement {
    effect = "Allow"

    actions = [
      "codebuild:BatchGetBuilds",
      "codebuild:StartBuild",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "codepipeline_policy" {
  name   = "codepipeline_policy"
  role   = aws_iam_role.codepipeline_role.id
  policy = data.aws_iam_policy_document.codepipeline_policy.json
}

// notification
resource "aws_sns_topic" "codepipeline" {
  name = "${var.env_code}-sns-codepipeline-state-change"
}

resource "aws_sns_topic_policy" "codepipeline" {
  arn    = aws_sns_topic.codepipeline.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

data "aws_iam_policy_document" "sns_topic_policy" {
  statement {
    effect  = "Allow"
    actions = ["sns:Publish"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = ["${aws_sns_topic.codepipeline.arn}"]
  }
}

resource "aws_cloudwatch_event_rule" "codepipeline" {
  name = "${var.env_code}-evt-rule-codepipeline-state-change"

  event_pattern = jsonencode({
    "source" = [
      "aws.codepipeline"
    ],
    "detail-type" = [
      "CodePipeline Pipeline Execution State Change"
    ]
  })
}

resource "aws_cloudwatch_event_target" "codepipeline_to_sns" {
  rule = aws_cloudwatch_event_rule.codepipeline.name
  arn  = aws_sns_topic.codepipeline.arn

  input_transformer {
    input_paths = {
      PipelineName = "$.detail.pipeline"
      State        = "$.detail.state"
    }

    input_template = "\"Pipeline [<PipelineName>] execution state changed [<State>]\""
  }
}
