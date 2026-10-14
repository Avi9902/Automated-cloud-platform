variable "project" {
  description = "Project name used in resource metadata."
  type        = string
}

variable "environment" {
  description = "Environment name, such as dev, staging, or prod."
  type        = string
}

variable "owner" {
  description = "Team responsible for the resources."
  type        = string
}

locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "Terraform"
  }
}

output "common_tags" {
  description = "Standard tags for resources managed by this project."
  value       = local.common_tags
}
