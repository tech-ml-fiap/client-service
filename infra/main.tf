########################
#  Rede padrão da conta
########################
data "aws_vpc" "default" { default = true }

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security-group liberando a porta da aplicação
resource "aws_security_group" "ecs_service" {
  name        = "${var.service_name}-sg"
  description = "Acesso público à aplicação"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = var.container_port
    to_port     = var.container_port
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

########################
#  IAM – Execution Role
########################
data "aws_iam_policy_document" "ecs_task_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_exec" {
  name               = "ecsTaskExecutionRole"      # mesmo nome usado nos tutoriais da AWS
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_policy" {
  role       = aws_iam_role.ecs_task_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

########################
#  CloudWatch Logs
########################
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.service_name}"
  retention_in_days = 7
}

########################
#  ECS Fargate
########################
resource "aws_ecs_cluster" "this" {
  name = "${var.service_name}-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family                   = var.service_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = local.execution_role_arn

  container_definitions = jsonencode([
    {
      name      = var.service_name
      image     = var.image_uri
      essential = true
      portMappings = [
        { containerPort = var.container_port, protocol = "tcp" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      environment = [
        { name = "DB_HOST",     value = var.db_host     },
        { name = "DB_PORT",     value = var.db_port     },
        { name = "DB_USER",     value = var.db_user     },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "DB_NAME",     value = var.db_name     }
      ]
    }
  ])
}

resource "aws_ecs_service" "app" {
  name            = var.service_name
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.app.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets         = data.aws_subnets.default.ids
    security_groups = [aws_security_group.ecs_service.id]
    assign_public_ip = true
  }

  lifecycle {
    ignore_changes = [task_definition] # Permite atualizar task via update-service
  }
}

########################
#  Run migrations após cada nova task definition
########################
resource "null_resource" "migrate" {
  triggers = {
    td_revision = aws_ecs_task_definition.app.revision
  }

  provisioner "local-exec" {
    command = <<EOT
    aws ecs run-task \
      --cluster ${aws_ecs_cluster.this.name} \
      --launch-type FARGATE \
      --task-definition ${aws_ecs_task_definition.app.arn} \
      --network-configuration "awsvpcConfiguration={subnets=[${join(",", data.aws_subnets.default.ids)}],securityGroups=[${aws_security_group.ecs_service.id}],assignPublicIp=ENABLED}" \
      --overrides '{"containerOverrides":[{"name":"${var.service_name}","command":["alembic","upgrade","head"]}]}'
    EOT
  }
}
