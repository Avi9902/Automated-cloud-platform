module "resource_metadata" {
  source = "../../modules/resource_metadata"


  project     = var.project_name
  environment = var.environment
  owner       = var.owner
}

output "common_tags" {
  description = "Standard tags for development infrastructure."
  value       = module.resource_metadata.common_tags
}
