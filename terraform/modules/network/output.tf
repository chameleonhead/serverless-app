output "vpc_id" {
  value = aws_vpc.main.id
}

output "subnet_private_db_ids" {
  value = [
    aws_subnet.private_db_az1.id,
    aws_subnet.private_db_az2.id,
    aws_subnet.private_db_az3.id
  ]
}
