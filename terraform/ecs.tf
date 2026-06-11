# ==========================================
# SECURITY GROUPS
# ==========================================
resource "aws_security_group" "alb_sg" {
  name        = "pyntar-alb-sg"
  vpc_id      = aws_vpc.frontend_vpc.id

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

resource "aws_security_group" "ecs_sg" {
  name        = "pyntar-ecs-sg"
  vpc_id      = aws_vpc.backend_vpc.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.frontend_vpc.cidr_block] # Proteksi ketat: Hanya menerima trafik eksklusif dari Frontend VPC
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # Akses keluar diperlukan untuk interaksi API GCP & Gemini
  }
}

# ==========================================
# APPLICATION LOAD BALANCER (ALB)
# ==========================================
resource "aws_lb" "pyntar_alb" {
  name               = "pyntar-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.frontend_pub_a.id, aws_subnet.frontend_pub_b.id]
}

resource "aws_lb_target_group" "ecs_tg" {
  name        = "pyntar-ecs-target-group"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.frontend_vpc.id
  target_type = "ip" # Wajib menggunakan mode IP untuk ECS Fargate lintas VPC Peering

  health_check {
    path                = "/"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200,302" # Mendukung redirect landing page Flask
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.pyntar_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_tg.arn
  }
}

# ==========================================
# AWS ECR REPOSITORY
# ==========================================
resource "aws_ecr_repository" "pyntar_repo" {
  name                         = "pyntar-backend"
  image_scanning_configuration { scan_on_push = true }
  tags                         = { Name = "Pyntar-ECR" }
}

# ==========================================
# ECS TASK EXECUTION IAM ROLE (Fixed Syntax)
# ==========================================
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRoleUAS"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_attach" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ==========================================
# MONITORING: CLOUDWATCH LOG GROUP
# ==========================================
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/pyntar-backend"
  retention_in_days = 7
}

# ==========================================
# ECS CLUSTER & SERVICE (FARGATE)
# ==========================================
resource "aws_ecs_cluster" "pyntar_cluster" {
  name = "pyntar-cluster"
}

resource "aws_ecs_task_definition" "pyntar_task" {
  family                   = "pyntar-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "pyntar-container"
      image     = "${aws_ecr_repository.pyntar_repo.repository_url}:latest"
      essential = true
      portMappings = [{
        containerPort = 8000
        hostPort      = 8000
      }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "flask"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "pyntar_service" {
  name            = "pyntar-service"
  cluster         = aws_ecs_cluster.pyntar_cluster.id
  task_definition = aws_ecs_task_definition.pyntar_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.backend_pub_a.id]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_tg.arn
    container_name   = "pyntar-container"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}