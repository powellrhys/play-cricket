variable "app_service_resource_group" {
  type        = string
  description = "The name of the Azure Resource Group to use."
  default     = ""
}

variable "app_service_location" {
  type        = string
  description = "The name of the Azure Location"
  default     = "westeurope"
}

variable "docker_image_name" {
  type        = string
  description = "The name of the Docker image"
  default     = ""
}
