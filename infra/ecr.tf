resource "aws_ecr_repository" "app_repository" {
  name = var.ecr_repo_name
  image_scanning_configuration { scan_on_push = true }
}

output "repo_url" {
  value       = aws_ecr_repository.app_repository.repository_url
  description = "URI do repositório ECR"
}
