
output "codebuild_arn" {
  value = aws_codebuild_project.build.arn
}

output "codepipeline_arn" {
  value = aws_codepipeline.codepipeline.arn
}
