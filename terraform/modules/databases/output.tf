output "apidb_cluster_identifier" {
  value = aws_rds_cluster.apidb.cluster_identifier
}

output "apidb_security_group_id" {
  value = aws_security_group.apidb.id
}

output "apidb_credential_secret_arn" {
  value = aws_rds_cluster.apidb.master_user_secret[0].secret_arn
}
