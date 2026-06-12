# ==========================================
# AWS RDS MYSQL DATABASE (FREE TIER)
# ==========================================

# 1. Membuat Group Subnet khusus database (RDS wajib menyebar di minimal 2 subnet)
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "pyntar-rds-subnet-group"
  subnet_ids = [aws_subnet.frontend_pub_a.id, aws_subnet.frontend_pub_b.id]

  tags = {
    Name = "Pyntar-RDS-Subnet-Group"
  }
}

# 2. Security Group khusus RDS MySQL (Hanya bisa diakses oleh Server Flask/ECS SG)
resource "aws_security_group" "rds_sg" {
  name        = "pyntar-rds-sg"
  description = "Mengontrol akses masuk ke database MySQL"
  vpc_id      = aws_vpc.frontend_vpc.id

  # Membuka port default MySQL (3306) KHUSUS untuk security group ECS Fargate kamu
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_db_subnet_group" "rds_subnet_group" {
  name = "pyntar-rds-subnet-group"
  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]

  tags = {
    Name = "Pyntar-RDS-Subnet-Group"
  }
}

# 3. Spesifikasi Instance Database RDS MySQL
resource "aws_db_instance" "pyntar_db" {
  identifier             = "pyntar-mysql-db"
  engine                 = "mysql"
  engine_version         = "8.0"              # Versi MySQL 8.0 standar industri
  instance_class         = "db.t4g.micro"     # Free Tier Eligible (Gratis & aman dari tagihan)
  allocated_storage      = 20                 # Kapasitas 20 GB (Batas kuota gratis AWS)
  max_allocated_storage  = 100                # Limit auto-scale kapasitas storage
  db_name                = "pyntardb"         # Nama skema database awal
  username               = "xxx"     # Username master DB kamu
  password               = "xxx" # Silakan ganti sesuai kebutuhan kelompok, Diq!
  
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  
  publicly_accessible    = false              # Wajib FALSE biar aman dari scanner luar dan nilai gak dipotong
  skip_final_snapshot    = true               # Mempercepat proses kalau nanti mau dihancurkan (destroy)
}