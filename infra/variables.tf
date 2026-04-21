variable "region" {
  type        = string
  description = "AWS region to deploy to"
  default     = "us-east-1"
}

variable "image_tag" {
  type        = string
  description = "Image tag for image in ECR repo to be used for lambda invocation"
  default     = "latest"
}

variable "codebuild_log_group" {
  type        = string
  description = "The log group for storing CodeBuild logs"
  default     = "codebuild-logs"
}

variable "github_repo_id" {
  type        = string
  description = "The Github repo to use as a source for codebuild"
  default     = "Emmanuel289/product-scanner"
}

variable "github_branch" {
  type        = string
  description = "The Github branch name for configuring CodeBuild"
  default     = "main"
}
