module "resource_metadata" {
  source = "../../modules/resource_metadata"

  project     = "cloud-agnostic-platform"
  environment = "dev"
  owner       = "platform-team"
}

output "common_tags" {
  description = "Standard tags for development infrastructure."
  value       = module.resource_metadata.common_tags
}
