# Create Code build bucket
data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "output" {
  bucket = "codebuild-output-${data.aws_caller_identity.current.account_id}"
}
# Create Assume Codebuild Assume Role Policy
data "aws_iam_policy_document" "codebuild_assume_role" {
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
  name               = "codebuild-role"
  assume_role_policy = data.aws_iam_policy_document.codebuild_assume_role.json
}

data "aws_iam_policy_document" "codestar_policy_document" {
  statement {
    effect = "Allow"
    actions = [
      "codeconnections:GetConnectionToken",
      "codeconnections:GetConnection"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "codestar_policy" {
  role   = aws_iam_role.codebuild_role.name
  policy = data.aws_iam_policy_document.codestar_policy_document.json
}


# ------------------------------------------------------------------------------
# Create Access Control for builds
# ------------------------------------------------------------------------------
data "aws_iam_policy_document" "cbd_build" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
    ]
    resources = ["*"]
  }
  statement {
    effect  = "Allow"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.output.arn,
      "${aws_s3_bucket.output.arn}/*"
    ]
  }
  statement {
    effect    = "Allow"
    actions   = ["ecr:*"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "cbd_build" {
  name        = "build"
  description = "Access Policy for Code build"
  policy      = data.aws_iam_policy_document.cbd_build.json
}

resource "aws_iam_role_policy_attachment" "cdb_build_access" {
  role       = aws_iam_role.codebuild_role.name
  policy_arn = aws_iam_policy.cbd_build.arn
}

resource "aws_iam_role_policy_attachment" "cpl_build_access" {
  role       = aws_iam_role.codepipeline_role.name
  policy_arn = aws_iam_policy.cbd_build.arn
}

# Create Assume Codepipeline Assume Role Policy
data "aws_iam_policy_document" "codepipeline_assume_role" {
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
  name               = "codepipeline-role"
  assume_role_policy = data.aws_iam_policy_document.codepipeline_assume_role.json
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
      aws_s3_bucket.output.arn,
      "${aws_s3_bucket.output.arn}/*"
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["codestar-connections:UseConnection"]
    resources = [aws_codestarconnections_connection.github.arn]
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


# Create Cloudwatch Log group for streaming Codebuild logs
resource "aws_cloudwatch_log_group" "build" {
  name = var.codebuild_log_group

  tags = {
    Environment = "dev"
    Application = "product-scanner"
  }
}
# Create CodeBuild Project
resource "aws_codebuild_project" "build" {
  name         = "build"
  description  = "Used to define the environment and commands for building the product scanner"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "runtime"
      value = "docker"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.build.name
      stream_name = "log-stream"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec.yml"

  }
}

# Create CodeStar Connection
resource "aws_codestarconnections_connection" "github" {
  name          = "github"
  provider_type = "GitHub"
}

# Create code pipeline
resource "aws_codepipeline" "codepipeline" {
  name     = "product-scanner-pipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.output.bucket
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
        ConnectionArn    = aws_codestarconnections_connection.github.arn
        FullRepositoryId = var.github_repo_id
        BranchName       = var.github_branch
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
        ProjectName = aws_codebuild_project.build.name
      }
    }
  }

}
