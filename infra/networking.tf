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

}

resource "aws_vpc" "main" {
  cidr_block           = local.vpc_cidr
  enable_dns_support   = local.enable_dns_support
  enable_dns_hostnames = local.enable_dns_hostnames
  tags = {
    Name  = local.vpc_name,
    Stack = local.stack_name,
    Env   = local.env
  }
}

# public
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  count                   = length(local.pub_cidrs)
  cidr_block              = element(local.pub_cidrs, count.index)
  availability_zone       = element(local.pub_avail_zones, count.index)
  map_public_ip_on_launch = local.pub_map_ip
  tags = {
    Name  = "${local.vpc_name}-${element(local.pub_avail_zones, count.index)}-public-subnet",
    Stack = local.stack_name,
    Env   = local.env
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name  = "${local.vpc_name}-igw",
    Stack = local.stack_name,
    Env   = local.env
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = {
    Name  = "${local.vpc_name}-public-route-table",
    Stack = local.stack_name,
    Env   = local.env
  }
}

resource "aws_route_table_association" "public" {
  count          = length(local.pub_cidrs)
  subnet_id      = element(aws_subnet.public.*.id, count.index)
  route_table_id = aws_route_table.public.id
}

# private
resource "aws_subnet" "private" {
  vpc_id                  = aws_vpc.main.id
  count                   = length(local.priv_cidrs)
  cidr_block              = element(local.priv_cidrs, count.index)
  availability_zone       = element(local.priv_avail_zones, count.index)
  map_public_ip_on_launch = local.priv_map_ip
  tags = {
    Name  = "${local.vpc_name}-${element(local.priv_avail_zones, count.index)}-private-subnet",
    Stack = local.stack_name,
    Env   = local.env
  }
}

resource "aws_eip" "nat_gw" {
  count = local.priv_nat_gateway ? 1 : 0
  domain = "vpc"
}

resource "aws_nat_gateway" "default" {
  count         = local.priv_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat_gw[count.index].id
  subnet_id     = element(aws_subnet.public.*.id, 0)
  depends_on    = [aws_internet_gateway.igw]
  tags = {
    Name  = "${local.vpc_name}-${element(local.priv_avail_zones, count.index)}-nat-gw",
    Stack = local.stack_name,
    Env   = local.env
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name  = "${local.vpc_name}-private-route-table",
    Stack = local.stack_name,
    Env   = local.env
  }
}

resource "aws_route" "private_nat_gateway" {
  count                  = local.priv_nat_gateway ? 1 : 0
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.default[count.index].id
}

resource "aws_route_table_association" "private" {
  count          = length(local.priv_cidrs)
  subnet_id      = element(aws_subnet.private.*.id, count.index)
  route_table_id = aws_route_table.private.id
}
