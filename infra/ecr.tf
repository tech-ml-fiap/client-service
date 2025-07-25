############################################################
# ECR para a imagem do serviço                             #
############################################################
resource "aws_ecr_repository" "app" {
  name = var.ecr_repo_name     # ex: "clientservice"

  image_scanning_configuration {
    scan_on_push = true
  }
}
