resource "aws_ecs_cluster" "main" {
  name = "${local.stack_name}-${local.env}"
}

resource "aws_ecs_service" "app" {
  name            = "${local.stack_name}-svc-${local.env}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 8501
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  lifecycle {
    ignore_changes = [
      desired_count
    ]
  }
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${local.stack_name}-app"
  network_mode             = "awsvpc" # containers share ENI
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "4096"
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
      dependsOn = [
        {
          containerName = "backend"
          condition     = "HEALTHY"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.frontend_container.name
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
      dependsOn = [
        {
          containerName = "mlflow"
          condition     = "HEALTHY"
        }
      ]
      healthCheck = {
        command     = ["CMD-SHELL", "python -c \"import sys,urllib.request; urllib.request.urlopen('http://localhost:8000/health'); sys.exit(0)\" || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.backend_container.name
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
      healthCheck = {
        command     = ["CMD-SHELL", "python -c \"import sys,urllib.request; urllib.request.urlopen('http://localhost:5000'); sys.exit(0)\" || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 30
      }
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.mlflow_container.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}
