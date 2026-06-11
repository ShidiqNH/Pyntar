# ==========================================
# A. FRONTEND VPC (Menerima Trafik Publik)
# ==========================================
resource "aws_vpc" "frontend_vpc" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_hostnames = true
  tags                 = { Name = "Pyntar-Frontend-VPC" }
}

resource "aws_subnet" "frontend_pub_a" {
  vpc_id            = aws_vpc.frontend_vpc.id
  cidr_block        = "10.1.1.0/24"
  availability_zone = "${var.region}a"
  tags              = { Name = "Frontend-Public-Subnet-A" }
}

resource "aws_subnet" "frontend_pub_b" {
  vpc_id            = aws_vpc.frontend_vpc.id
  cidr_block        = "10.1.2.0/24"
  availability_zone = "${var.region}b"
  tags              = { Name = "Frontend-Public-Subnet-B" }
}

resource "aws_internet_gateway" "frontend_igw" {
  vpc_id = aws_vpc.frontend_vpc.id
}

resource "aws_route_table" "frontend_rt" {
  vpc_id = aws_vpc.frontend_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.frontend_igw.id
  }
}

resource "aws_route_table_association" "frontend_rta_a" {
  subnet_id      = aws_subnet.frontend_pub_a.id
  route_table_id = aws_route_table.frontend_rt.id
}

resource "aws_route_table_association" "frontend_rta_b" {
  subnet_id      = aws_subnet.frontend_pub_b.id
  route_table_id = aws_route_table.frontend_rt.id
}

# ==========================================
# B. BACKEND VPC (Tempat ECS Fargate Flask Berada)
# ==========================================
resource "aws_vpc" "backend_vpc" {
  cidr_block           = "10.2.0.0/16"
  enable_dns_hostnames = true
  tags                 = { Name = "Pyntar-Backend-VPC" }
}

resource "aws_subnet" "backend_pub_a" {
  vpc_id            = aws_vpc.backend_vpc.id
  cidr_block        = "10.2.1.0/24"
  availability_zone = "${var.region}a"
  tags              = { Name = "Backend-Subnet-A" }
}

resource "aws_internet_gateway" "backend_igw" {
  vpc_id = aws_vpc.backend_vpc.id
}

resource "aws_route_table" "backend_rt" {
  vpc_id = aws_vpc.backend_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.backend_igw.id
  }
}

resource "aws_route_table_association" "backend_rta" {
  subnet_id      = aws_subnet.backend_pub_a.id
  route_table_id = aws_route_table.backend_rt.id
}

# ==========================================
# C. VPC PEERING (Jembatan Lintas Jaringan)
# ==========================================
resource "aws_vpc_peering_connection" "fb_peering" {
  peer_vpc_id = aws_vpc.backend_vpc.id
  vpc_id      = aws_vpc.frontend_vpc.id
  auto_accept = true
  tags        = { Name = "Frontend-to-Backend-Peering" }
}

resource "aws_route" "frontend_to_backend" {
  route_table_id            = aws_route_table.frontend_rt.id
  destination_cidr_block    = aws_vpc.backend_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.fb_peering.id
}

resource "aws_route" "backend_to_frontend" {
  route_table_id            = aws_route_table.backend_rt.id
  destination_cidr_block    = aws_vpc.frontend_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.fb_peering.id
}