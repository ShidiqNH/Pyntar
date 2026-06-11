# ECS Cluster
resource "aws_ecs_cluster" "pyntar_cluster" {
  name = "pyntar-cluster"
}

# IAM Role (wajib)
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2008-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Task Definition (INI YANG KAMU TANYA 🔥)
resource "aws_ecs_task_definition" "pyntar_task" {
  family                   = "pyntar-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"

  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "pyntar-container"
      image = "${aws_ecr_repository.pyntar_repo.repository_url}:latest"

      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "pyntar_service" {
  name            = "pyntar-service"
  cluster         = aws_ecs_cluster.pyntar_cluster.id
  task_definition = aws_ecs_task_definition.pyntar_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = ["subnet-xxxxxx"] # nanti diganti
    assign_public_ip = true
  }
}