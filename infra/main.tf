module "frontend" {
    source = "git::https://github.com/powellrhys/powellrhys-iac.git//terraform/azure/app_service?ref=feature/play-cricket-debugging"

    name                = "play-cricket-streamlit-frontend"
    resource_group_name = var.app_service_resource_group
    location            = var.location
    app_service_plan_id = data.azurerm_app_service_plan.app_service_plan.id
    docker_image        = var.docker_image_name
    docker_image_tag    = "latest"
}
