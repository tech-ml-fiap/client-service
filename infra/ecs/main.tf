###############################################
#  VPC default e sub-redes públicas           #
###############################################
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

###############################################
#  IAM – LabRole                               #
###############################################
data "aws_iam_role" "lab" {
  name = var.exec_role_name
}

###############################################
#  CloudWatch Logs                             #
###############################################
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.service_name}"
  retention_in_days = 7
}

###############################################
#  Security-Groups                             #
###############################################
# ALB SG
resource "aws_security_group" "alb_sg" {
  name        = "${var.service_name}-alb-sg"
  description = "Public HTTP access"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Tasks SG
resource "aws_security_group" "task_sg" {
  name        = "${var.service_name}-task-sg"
  description = "Traffic from ALB"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

###############################################
#  ECS Cluster & Task Definition               #
###############################################
resource "aws_ecs_cluster" "this" {
  name = "${var.service_name}-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family                   = var.service_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = data.aws_iam_role.lab.arn

  container_definitions = jsonencode([
    {
      name  = var.service_name
      image = var.image_uri
      essential = true
      portMappings = [
        { containerPort = var.container_port, protocol = "tcp" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options   = {
          awslogs-group         = aws_cloudwatch_log_group.app.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      environment = [
        { name = "DB_HOST",     value = var.db_host },
        { name = "DB_PORT",     value = var.db_port },
        { name = "DB_USER",     value = var.db_user },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "DB_NAME",     value = var.db_name }
      ]
    }
  ])
}

###############################################
#  Application Load Balancer                  #
###############################################
resource "aws_lb" "app" {
  name               = "${var.service_name}-alb"
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = data.aws_subnets.public.ids
}

resource "aws_lb_target_group" "tg" {
  name        = "${var.service_name}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/health"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

###############################################
#  ECS Service                                #
###############################################
resource "aws_ecs_service" "app" {
  name            = var.service_name
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    assign_public_ip = false
    subnets          = data.aws_subnets.public.ids
    security_groups  = [aws_security_group.task_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.tg.arn
    container_name   = var.service_name
    container_port   = var.container_port
  }

  lifecycle {
    ignore_changes = [task_definition]  # permite atualizar TD sem recriar Service
  }
}

###############################################
#  Migrações (alembic upgrade head)           #
###############################################
resource "null_resource" "migrate" {
  triggers = { rev = aws_ecs_task_definition.app.revision }

  provisioner "local-exec" {
    command = <<EOT
aws ecs run-task \
  --cluster ${aws_ecs_cluster.this.name} \
  --launch-type FARGATE \
  --task-definition ${aws_ecs_task_definition.app.arn} \
  --network-configuration "awsvpcConfiguration={subnets=[${join(",", data.aws_subnets.public.ids)}],securityGroups=[${aws_security_group.task_sg.id}],assignPublicIp=ENABLED}" \
  --overrides '{"containerOverrides":[{"name":"${var.service_name}","command":["alembic","upgrade","head"]}]}'
EOT
  }
}

