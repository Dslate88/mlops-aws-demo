locals {
  stack_name = "mlops-demo"
  env        = "dev"

  # vpc
  vpc_name             = "${local.env}-${local.stack_name}"
  vpc_cidr             = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  pub_cidrs       = ["10.0.0.0/24", "10.0.2.0/24"]
  pub_avail_zones = ["us-east-1a", "us-east-1b"]
  pub_map_ip      = true

  priv_cidrs       = ["10.0.1.0/24", "10.0.3.0/24"]
  priv_avail_zones = ["us-east-1a", "us-east-1b"]
  priv_map_ip      = false
  priv_nat_gateway = true

  # ecr
  ecr_containers = ["${local.stack_name}-frontend", "${local.stack_name}-backend", "${local.stack_name}-mlflow"]

  # r53
  domain_name = "devinslate.com"
  subdomain   = "mlops-demo"

}

## Setup ECR
resource "aws_ecr_repository" "containers" {
  for_each             = toset(local.ecr_containers)
  name                 = each.value
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

## CW for ECS
resource "aws_cloudwatch_log_group" "backend_container" {
  name              = "/ecs/${local.stack_name}/${local.env}-backend"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "frontend_container" {
  name              = "/ecs/${local.stack_name}/${local.env}-frontend"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "mlflow_container" {
  name              = "/ecs/${local.stack_name}/${local.env}-mlfow"
  retention_in_days = 14
}

resource "aws_ecr_lifecycle_policy" "webapp" {
  for_each   = aws_ecr_repository.containers
  repository = each.value.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "keep last 10 images"
      action = {
        type = "expire"
      }
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
    }]
  })
}

