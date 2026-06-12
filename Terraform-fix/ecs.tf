# 1. ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-ecs-cluster"
}

# 2. IAM Role untuk ECS (Execution & Task Role)
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# 3. Cloudwatch Log Group untuk Flask logs
resource "aws_cloudwatch_log_group" "flask_logs" {
  name              = "/ecs/flask-app"
  retention_in_days = 7
}

# 4. Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "flask-app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name      = "flask-app"
    image     = var.flask_app_image != "" ? var.flask_app_image : "nginx:latest"
    essential = true
    portMappings = [{
      containerPort = var.flask_app_image != "" ? 5000 : 80
      hostPort      = var.flask_app_image != "" ? 5000 : 80
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.flask_logs.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
    environment = [
      # Database Configs
      { name = "DATABASE_HOST", value = aws_db_instance.mysql.address },
      { name = "DATABASE_NAME", value = aws_db_instance.mysql.db_name },
      { name = "DATABASE_USER", value = var.db_username },
      { name = "DATABASE_PASSWORD", value = var.db_password },
      
      # Cloudflare R2 Configs
      { name = "R2_BUCKET_NAME", value = cloudflare_r2_bucket.media_bucket.name },
      { name = "R2_ACCOUNT_ID", value = var.cloudflare_account_id },
      { name = "R2_ACCESS_KEY_ID", value = var.cloudflare_access_key },
      { name = "R2_SECRET_ACCESS_KEY", value = var.cloudflare_secret_key },

      # PERBAIKAN: Menyuntikkan Gemini API Key ke runtime kontainer secara aman
      { name = "GEMINI_API_KEY", value = var.gemini_api_key }
    ]
  }])
}

# 5. Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "app" {
  name        = "${var.environment}-tg"
  port        = var.flask_app_image != "" ? 5000 : 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/" # Memaksa AWS mengecek kesehatan ke halaman utama landing page
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# 6. ECS Service
resource "aws_ecs_service" "main" {
  name            = "${var.environment}-flask-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "flask-app"
    container_port   = var.flask_app_image != "" ? 5000 : 80
  }

  depends_on = [aws_lb_listener.http]
}