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
  priv_map_ip      = true
  priv_nat_gateway = true

  ecr_containers = ["${local.stack_name}-frontend", "${local.stack_name}-backend"]

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

