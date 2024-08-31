output "frontend_domain_name" {
  value = "https://${module.frontend.cloudfront_endpoint}"
}
