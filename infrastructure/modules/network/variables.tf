variable "name" {
  description = "Name prefix for network resources."
  type        = string
}

variable "vpc_cidr" {
  description = "IPv4 CIDR block for the VPC."
  type        = string
}

variable "availability_zones" {
  description = "Availability zones used for the network."
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "Provide at least two availability zones for resilience."
  }
}

variable "public_subnet_cidrs" {
  description = "IPv4 CIDR blocks for public subnets, one per availability zone."
  type        = list(string)

  validation {
    condition     = length(var.public_subnet_cidrs) == length(var.availability_zones)
    error_message = "Provide exactly one public subnet CIDR per availability zone."
  }
}

variable "private_subnet_cidrs" {
  description = "IPv4 CIDR blocks for private subnets, one per availability zone."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_cidrs) == length(var.availability_zones)
    error_message = "Provide exactly one private subnet CIDR per availability zone."
  }
}

variable "tags" {
  description = "Common tags applied to network resources."
  type        = map(string)
  default     = {}
}
