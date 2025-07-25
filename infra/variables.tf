variable "aws_region" {
  description = "Região AWS onde os recursos serão criados"
  type        = string
  default     = "us-east-1"
}

variable "db_host" {
  description = "Endpoint do RDS"
  type        = string
}

variable "db_port" {
  description = "Porta do RDS"
  type        = string
  default     = "5432"
}

variable "db_user" {
  description = "Usuário do banco"
  type        = string
}

variable "db_password" {
  description = "Senha do banco"
  type        = string
}

variable "db_name" {
  description = "Nome do schema/banco"
  type        = string
}

variable "cluster_name" {
  description = "Nome do cluster ECS"
  type        = string
  default     = "clientservice-cluster"
}

variable "service_name" {
  description = "Nome do ECS Service e da Task Definition"
  type        = string
  default     = "clientservice-svc"
}

variable "container_port" {
  description = "Porta exposta pelo container"
  type        = number
  default     = 8000
}

variable "ecr_repo_name" {
  description = "Nome do repositório ECR"
  type        = string
  default     = "clientservice"
}

variable "image_uri" {
  type        = string
}

variable "cpu" {
  type        = number
  default         = 256
}

variable "memory" {
  type        = number
  default         = 512
}

variable "execution_role" {
  type        = string
  default = "arn:aws:iam::049015295261:role/LabRole"
}

variable "exec_role_name" {
  description = "Nome da LabRole existente (padrão do AWS Academy)"
  type        = string
}
