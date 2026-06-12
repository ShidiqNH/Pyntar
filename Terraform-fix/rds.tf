resource "aws_db_subnet_group" "main" {
  name       = "${var.environment}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  tags       = { Name = "Main DB Subnet Group" }
}

resource "aws_db_instance" "mysql" {
  identifier             = "${var.environment}-flask-db"
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "mysql"
  engine_version         = "8.0"          # Menggunakan MySQL versi 8.0
  instance_class         = "db.t4g.micro" # Instance kelas t4g ramah di kantong
  db_name                = "flask_db"
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  skip_final_snapshot    = true
}