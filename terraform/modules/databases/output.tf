output "apidb_security_group_id" {
  value = aws_security_group.apidb.id
}

output "apidb_resource_id" {
  value = aws_rds_cluster.apidb.cluster_resource_id
}

output "apidb_host" {
  value = aws_rds_cluster.apidb.endpoint
}
