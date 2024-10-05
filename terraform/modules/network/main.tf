data "aws_region" "current" {
}

resource "aws_vpc_dhcp_options" "main" {
  domain_name         = "${data.aws_region.current.name}.compute.internal"
  domain_name_servers = ["AmazonProvidedDNS"]
  tags = {
    Name = "${var.env_code}-dhcp-options"
  }
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "${var.env_code}-vpc-01"
  }
}

resource "aws_subnet" "private_db_az1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${data.aws_region.current.name}c"
  tags = {
    Name = "${var.env_code}-vpc-01-subnet-private-db-az1"
  }
}

resource "aws_subnet" "private_db_az2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${data.aws_region.current.name}d"
  tags = {
    Name = "${var.env_code}-vpc-01-subnet-private-db-az2"
  }
}

resource "aws_subnet" "private_db_az3" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "${data.aws_region.current.name}a"
  tags = {
    Name = "${var.env_code}-vpc-01-subnet-private-db-az3"
  }
}

resource "aws_network_acl" "private_db" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.env_code}-vpc-01-nacl-private-db"
  }
}

resource "aws_network_acl_association" "private_db_az1" {
  subnet_id      = aws_subnet.private_db_az1.id
  network_acl_id = aws_network_acl.private_db.id
}

resource "aws_network_acl_association" "private_db_az2" {
  subnet_id      = aws_subnet.private_db_az2.id
  network_acl_id = aws_network_acl.private_db.id
}

resource "aws_network_acl_association" "private_db_az3" {
  subnet_id      = aws_subnet.private_db_az3.id
  network_acl_id = aws_network_acl.private_db.id
}



resource "aws_subnet" "private_lambda_az1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "${data.aws_region.current.name}c"
  tags = {
    Name = "${var.env_code}-vpc-01-subnet-private-lambda-az1"
  }
}

resource "aws_subnet" "private_lambda_az2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.5.0/24"
  availability_zone = "${data.aws_region.current.name}d"
  tags = {
    Name = "${var.env_code}-vpc-01-subnet-private-lambda-az2"
  }
}

resource "aws_subnet" "private_lambda_az3" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.6.0/24"
  availability_zone = "${data.aws_region.current.name}a"
  tags = {
    Name = "${var.env_code}-vpc-01-subnet-private-lambda-az3"
  }
}

resource "aws_network_acl" "private_lambda" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.env_code}-vpc-01-nacl-private-lambda"
  }
}

resource "aws_network_acl_association" "private_lambda_az1" {
  subnet_id      = aws_subnet.private_lambda_az1.id
  network_acl_id = aws_network_acl.private_lambda.id
}

resource "aws_network_acl_association" "private_lambda_az2" {
  subnet_id      = aws_subnet.private_lambda_az2.id
  network_acl_id = aws_network_acl.private_lambda.id
}

resource "aws_network_acl_association" "private_lambda_az3" {
  subnet_id      = aws_subnet.private_lambda_az3.id
  network_acl_id = aws_network_acl.private_lambda.id
}
