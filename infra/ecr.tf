# infra/ecr.tf

resource "aws_ecr_repository" "app" {
  name                 = var.ecr_repo_name       # defina em variables.tf
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Environment = "production"
    Service     = var.service_name
  }
}
