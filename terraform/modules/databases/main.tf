resource "aws_db_subnet_group" "apidb" {
  name       = "${var.env_code}-db-subnet-group-api"
  subnet_ids = var.db_subnet_ids

  tags = {
    Name = "${var.env_code}-db-subnet-group-api"
  }
}

resource "aws_rds_cluster_parameter_group" "apidb" {
  name   = "${var.env_code}-rds-parameter-group-api"
  family = "aurora-postgresql16"
  tags = {
    Name = "${var.env_code}-rds-parameter-group-api"
  }
}

resource "aws_db_parameter_group" "apidb" {
  name   = "${var.env_code}-db-parameter-group-api"
  family = "aurora-postgresql16"
  tags = {
    Name = "${var.env_code}-db-parameter-group-api"
  }
}

resource "aws_rds_cluster" "apidb" {
  cluster_identifier                  = "${var.env_code}-rds-api"
  engine                              = "aurora-postgresql"
  engine_mode                         = "provisioned"
  engine_version                      = "16.1"
  db_cluster_parameter_group_name     = aws_rds_cluster_parameter_group.apidb.name
  storage_encrypted                   = true
  master_username                     = "postgres"
  manage_master_user_password         = true
  db_subnet_group_name                = aws_db_subnet_group.apidb.name
  enable_http_endpoint                = true
  iam_database_authentication_enabled = true
  performance_insights_enabled        = true
  backup_retention_period             = 14
  backtrack_window                    = 0
  copy_tags_to_snapshot               = true
  preferred_backup_window             = "14:00-14:30"
  preferred_maintenance_window        = "sun:16:00-sun:16:30"
  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 1
  }
}


resource "aws_rds_cluster_instance" "apidb_instance1" {
  cluster_identifier      = aws_rds_cluster.apidb.id
  identifier              = "${var.env_code}-rds-api-instance-1"
  engine                  = aws_rds_cluster.apidb.engine
  engine_version          = aws_rds_cluster.apidb.engine_version
  db_parameter_group_name = aws_db_parameter_group.apidb.name
  instance_class          = "db.serverless"
  promotion_tier          = 1
}
