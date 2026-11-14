variable "region" {
  type        = string
  description = "AWS region to deploy to"
}

variable "profile" {
  type        = string
  description = "AWS profile to use"
}

variable "image_tag" {
  type        = string
  description = "Image tag for image in ECR repo to be used for lambda invocation"
}

variable "codebuild_log_group" {
  type        = string
  description = "The log group for storing CodeBuild logs"
}

variable "github_repo_id" {
  type        = string
  description = "The Github repo to use as a source for codebuild"
}

variable "github_branch" {
  type        = string
  description = "The Github branch name for configuring CodeBuild"
}


variable "cognito_user_pool_name" {
  type        = string
  description = "The Cognito userpool for authorizing users"
}


variable "custom_domain" {
  type        = string
  description = "The custom domain name for sign up and sign in pages"
}

variable "call_back_urls" {
  type        = list(string)
  description = "List of allowed callback urls for the identity providers"
}
