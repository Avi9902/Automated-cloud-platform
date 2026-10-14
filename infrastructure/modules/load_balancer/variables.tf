variable "name" {
  description = "Name prefix for the application load balancer."
  type        = string
}

variable "vpc_id" {
  description = "VPC where the load balancer target group will operate."
  type        = string
}

variable "subnet_ids" {
  description = "Public subnet IDs for the internet-facing load balancer."
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "The load balancer requires at least two subnets."
  }
}

variable "security_group_id" {
  description = "Security group attached to the load balancer."
  type        = string
}

variable "target_port" {
  description = "Port used by the application targets."
  type        = number
  default     = 8080
}

variable "health_check_path" {
  description = "HTTP health check path for application targets."
  type        = string
  default     = "/healthz"
}

variable "tags" {
  description = "Tags applied to load balancer resources."
  type        = map(string)
  default     = {}
}
