output "auth_function_domain_name" {
  value = "${aws_lambda_function_url.auth_url.url_id}.lambda-url.${data.aws_region.current.name}.on.aws"
}
