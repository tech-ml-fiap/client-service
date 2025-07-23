terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.50" }
  }
}

provider "aws" {
  region = var.aws_region
}

# ---------------- VPC + Subnets ----------------
module "network" {
  source  = "terraform-aws-modules/vpc/aws"
  name    = "clientservice-vpc"
  cidr    = "10.0.0.0/16"
  azs     = ["us-east-1a", "us-east-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]
  enable_nat_gateway = true
}

# ---------------- RDS PostgreSQL ----------------
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  engine            = "postgres"
  engine_version    = "15.6"
  identifier        = "clientservice-db"
  instance_class    = "db.t4g.micro"
  allocated_storage = 20
  username = var.db_username
  password = var.db_password
  db_subnet_group_name = module.network.database_subnet_group_name
  vpc_security_group_ids = [module.network.default_security_group_id]
  publicly_accessible    = false
}

# ---------------- ECR ----------------
resource "aws_ecr_repository" "this" {
  name = var.ecr_repo_name
  image_scanning_configuration { scan_on_push = true }
  lifecycle_policy            = jsonencode({ /* opcional */ })
}

# ---------------- ECS Cluster ----------------
module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  name    = "clientservice-cluster"
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
}

# ---------------- ALB ----------------
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  name    = "clientservice-alb"
  load_balancer_type = "application"
  vpc_id             = module.network.vpc_id
  subnets            = module.network.public_subnets
  security_groups    = [module.network.default_security_group_id]
  target_groups = [{ name_prefix = "client", port = 8000, protocol = "HTTP" }]
  listeners = [{
    port               = 80
    protocol           = "HTTP"
    default_action = {
      type             = "forward"
      target_group_index = 0
    }
  }]
}

# ---------------- ECS Task Definition ----------------
resource "aws_ecs_task_definition" "app" {
  family                   = "clientservice"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu    = 256
  memory = 512
  execution_role_arn = aws_iam_role.ecs_exec.arn
  task_role_arn      = aws_iam_role.ecs_exec.arn

  container_definitions = jsonencode([
    {
      name  = "app"
      image = "IMAGE_URI"   # substituído pelo workflow
      portMappings = [{ containerPort = 8000, protocol = "tcp" }]
      environment  = [
        { name = "DB_HOST",     value = module.db.db_instance_address },
        { name = "DB_PORT",     value = module.db.db_instance_port },
        { name = "DB_USER",     value = var.db_username },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "DB_NAME",     value = module.db.db_name },
      ]
    }
  ])
}

# ---------------- ECS Service ----------------
resource "aws_ecs_service" "svc" {
  name            = "clientservice-svc"
  cluster         = module.ecs.cluster_id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = module.network.private_subnets
    security_groups  = [module.network.default_security_group_id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = module.alb.target_groups[0].arn
    container_name   = "app"
    container_port   = 8000
  }
}
