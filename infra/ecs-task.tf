resource "aws_ecs_task_definition" "this" {
  family                   = var.service_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"

  execution_role_arn = aws_iam_role.ecs_execution.arn   # << aqui!
  task_role_arn      = aws_iam_role.ecs_execution.arn   # opcional, se a task precisar

  container_definitions = jsonencode([
    {
      name  = var.service_name
      image = aws_ecr_repository.app.repository_url
      portMappings = [
        { containerPort = var.container_port, protocol = "tcp" }
      ]
      environment = [
        { name = "DB_HOST",     value = var.db_host     },
        { name = "DB_PORT",     value = var.db_port     },
        { name = "DB_USER",     value = var.db_user     },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "DB_NAME",     value = var.db_name     },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${var.service_name}"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}
