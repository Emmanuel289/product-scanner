variable "codebuild_log_group" {
  type        = string
  description = "The log group for storing CodeBuild logs"
}

variable "github_repo_id" {
  type        = string
  description = "The Github repo for configuring CodeBuild"
  default     = "Emmanuel289/product-scanner"
}

variable "github_branch" {
  type        = string
  description = "The Github branch name for configuring CodeBuild"
  default     = "main"
}

variable "codebuild_bucket" {
  type        = string
  description = "S3 bucket for storing Codebuild output artifacts"
  default     = "codebuild-output"
}
