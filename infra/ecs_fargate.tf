resource "aws_ecs_cluster" "main" {
  name = "${local.stack_name}-${local.env}"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${local.stack_name}-app"
  network_mode             = "awsvpc" # containers share ENI
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "frontend"
      image     = "${aws_ecr_repository.containers["${local.stack_name}-frontend"].repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8501
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "BACKEND_URL"
          value = "http://localhost:8000/chat"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${local.stack_name}-frontend"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    },
    {
      name      = "backend"
      image     = "${aws_ecr_repository.containers["${local.stack_name}-backend"].repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "MLFLOW_TRACKING_URI"
          value = "http://localhost:5000"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${local.stack_name}-backend"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    },
    {
      name      = "mlflow"
      image     = "ghcr.io/mlflow/mlflow:v3.6.0"
      essential = true
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]
      command = [
        "mlflow",
        "server",
        "--backend-store-uri", "sqlite:///mlflow.db",
        "--default-artifact-root", "/mlruns",
        "--host", "0.0.0.0",
        "--port", "5000"
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${local.stack_name}-mlflow"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

