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

resource "aws_network_acl_rule" "private_db_ingress_allow_all" {
  network_acl_id = aws_network_acl.private_db.id
  rule_number    = 100
  rule_action    = "allow"
  egress         = false
  cidr_block     = "0.0.0.0/0"
  protocol       = -1
}

resource "aws_network_acl_rule" "private_db_egress_allow_all" {
  network_acl_id = aws_network_acl.private_db.id
  rule_number    = 100
  rule_action    = "allow"
  egress         = true
  cidr_block     = "0.0.0.0/0"
  protocol       = -1
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

resource "aws_network_acl_rule" "private_lambda_ingress_allow_all" {
  network_acl_id = aws_network_acl.private_lambda.id
  rule_number    = 100
  rule_action    = "allow"
  egress         = false
  cidr_block     = "0.0.0.0/0"
  protocol       = -1
}

resource "aws_network_acl_rule" "private_lambda_egress_allow_all" {
  network_acl_id = aws_network_acl.private_lambda.id
  rule_number    = 100
  rule_action    = "allow"
  egress         = true
  cidr_block     = "0.0.0.0/0"
  protocol       = -1
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

resource "aws_subnet" "private_cicd_az1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.7.0/24"
  availability_zone = "${data.aws_region.current.name}c"
  tags = {
    Name = "${var.env_code}-vpc-01-subnet-private-cicd-az1"
  }
}

resource "aws_network_acl" "private_cicd" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.env_code}-vpc-01-nacl-private-cicd"
  }
}

resource "aws_network_acl_rule" "private_cicd_ingress_allow_all" {
  network_acl_id = aws_network_acl.private_cicd.id
  rule_number    = 100
  rule_action    = "allow"
  egress         = false
  cidr_block     = "0.0.0.0/0"
  protocol       = -1
}

resource "aws_network_acl_rule" "private_cicd_egress_allow_all" {
  network_acl_id = aws_network_acl.private_cicd.id
  rule_number    = 100
  rule_action    = "allow"
  egress         = true
  cidr_block     = "0.0.0.0/0"
  protocol       = -1
}

resource "aws_network_acl_association" "private_cicd_az1" {
  subnet_id      = aws_subnet.private_cicd_az1.id
  network_acl_id = aws_network_acl.private_cicd.id
}

resource "aws_subnet" "public_az1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.253.0/24"
  availability_zone = "${data.aws_region.current.name}c"
  tags = {
    Name = "${var.env_code}-vpc-01-subnet-public-az1"
  }
}

resource "aws_network_acl" "public" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.env_code}-vpc-01-nacl-public"
  }
}

resource "aws_network_acl_rule" "public_ingress_allow_all" {
  network_acl_id = aws_network_acl.public.id
  rule_number    = 100
  rule_action    = "allow"
  egress         = false
  cidr_block     = "0.0.0.0/0"
  protocol       = -1
}
resource "aws_network_acl_rule" "public_egress_allow_all" {
  network_acl_id = aws_network_acl.public.id
  rule_number    = 100
  rule_action    = "allow"
  egress         = true
  cidr_block     = "0.0.0.0/0"
  protocol       = -1
}

resource "aws_network_acl_association" "public_az1" {
  subnet_id      = aws_subnet.public_az1.id
  network_acl_id = aws_network_acl.public.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.env_code}-vpc-01-rtb-public"
  }
}

resource "aws_route_table_association" "public_az1" {
  subnet_id      = aws_subnet.public_az1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_internet_gateway" "main" {
  tags = {
    Name = "${var.env_code}-vpc-01-igw"
  }
}

resource "aws_internet_gateway_attachment" "main" {
  vpc_id              = aws_vpc.main.id
  internet_gateway_id = aws_internet_gateway.main.id
}

resource "aws_route" "public_igw" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

resource "aws_eip" "public_nat_az1" {
  tags = {
    Name = "${var.env_code}-vpc-01-eip-nat-1"
  }
}

resource "aws_nat_gateway" "public_nat_az1" {
  subnet_id     = aws_subnet.public_az1.id
  allocation_id = aws_eip.public_nat_az1.id
  tags = {
    Name = "${var.env_code}-vpc-01-nat-az1"
  }
}

resource "aws_route" "private_to_public_az1" {
  route_table_id         = aws_vpc.main.main_route_table_id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.public_nat_az1.id
}
