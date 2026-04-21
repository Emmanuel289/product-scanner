
# Codebuild IAM role
data "aws_iam_policy_document" "assume_role" {
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
  name               = "build"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
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

# Log group
resource "aws_cloudwatch_log_group" "build" {
  name = "product-scanner-build"

  tags = {
    Environment = "dev"
    Application = "product-scanner"
  }
}
# CodeBuild project
resource "aws_codebuild_project" "build" {
  name         = "product-scanner-build"
  description  = "Used to define the environment and commands for building the product scanner"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "NO_ARTIFACTS"
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
    type            = "GITHUB"
    location        = "https://github.com/Emmanuel289/product-scanner.git"
    git_clone_depth = 1
    git_submodules_config {
      fetch_submodules = true
    }

  }
}
