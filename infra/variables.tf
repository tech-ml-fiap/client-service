variable "aws_region"           { type = string default = "us-east-1" }
variable "ecr_repo_name"        { type = string default = "clientservice" }

variable "cluster_name"         { type = string default = "clientservice-cluster" }
variable "service_name"         { type = string default = "clientservice-svc" }
variable "container_port"       { type = number default = 8000 }

# DB connection (injected via secrets)
variable "db_host"              { type = string }
variable "db_port"              { type = string }
variable "db_user"              { type = string }
variable "db_password"          { type = string }
variable "db_name"              { type = string }

# IAM execution role pré‑existente
variable "execution_role_arn"   { type = string }