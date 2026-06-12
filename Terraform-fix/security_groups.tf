# ALB Security Group (Terbuka ke Publik)
resource "aws_security_group" "alb" {
  name        = "${var.environment}-alb-sg"
  description = "Allow HTTP inbound traffic"
  vpc_id      = aws_vpc.main.id

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

# ECS Security Group (Hanya menerima traffic dari ALB)
resource "aws_security_group" "ecs_tasks" {
  name        = "${var.environment}-ecs-tasks-sg"
  description = "Allow inbound traffic from ALB only"
  vpc_id      = aws_vpc.main.id

  # Mengizinkan port 80 (untuk placeholder Nginx saat pertama kali apply)
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Mengizinkan port 5000 (untuk aplikasi Flask asli kamu via GitHub Actions)
  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS Security Group (Hanya menerima traffic dari ECS Tasks lewat port MySQL)
resource "aws_security_group" "db" {
  name   = "${var.environment}-db-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 3306 # Diubah ke 3306 untuk MySQL
    to_port         = 3306 # Diubah ke 3306 untuk MySQL
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id] # Hanya bisa diakses oleh ECS
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}