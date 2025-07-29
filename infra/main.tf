###############################################################################
# Terraform – ECR (apenas repositório)
###############################################################################
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = "us-east-1"
}

#############################
# Variável para reaproveitar nome
#############################
variable "ecr_repo_name" {
  description = "Nome do repositório ECR"
  type        = string
  default     = "customer-service"   # altere se precisar
}

#############################
# Repositório ECR
#############################
resource "aws_ecr_repository" "repo" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"

  # Política de expurgo opcional – mantém só as 20 últimas imagens
  lifecycle_policy {
    policy = jsonencode({
      rules = [{
        rulePriority = 1
        description  = "Keep last 20 images"
        selection = {
          tagStatus     = "any"
          countType     = "imageCountMoreThan"
          countNumber   = 20
          countUnit     = "images"
        }
        action = { type = "expire" }
      }]
    })
  }
}

#############################
# Saída útil para o workflow
#############################
output "repository_uri" {
  value       = aws_ecr_repository.repo.repository_url
  description = "URI completo do repositório (ACCOUNT.dkr.ecr.REGION.amazonaws.com/NAME)"
}
