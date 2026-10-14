variable "aws_region" {
  description = "AWS region approved for this environment."
  type        = string
}

variable "project_name" {
  description = "Project name used for resource metadata."
  type        = string
  default     = "cloud-agnostic-platform"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Team responsible for the resources."
  type        = string
  default     = "platform-team"
}
