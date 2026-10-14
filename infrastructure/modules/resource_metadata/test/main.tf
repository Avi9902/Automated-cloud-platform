module "metadata" {
  source = "./.."

  project     = "cloud-agnostic-platform"
  environment = "dev"
  owner       = "platform-team"
}

output "test_tags" {
  value = module.metadata.common_tags
}
