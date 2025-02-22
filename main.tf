terraform {
  required_version = ">= 1.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.00.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "rg-anoopkumar-3792_ai"
    storage_account_name = "saterraformstaterxt"  # Replace with your Azure storage account name
    container_name       = "terraformstate"             # Replace with your container name if different
    key                  = "terraform.tfstate"          # The state file name
  }
}
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "anoopp_rg08" {
  name     = "anoopp-rg08"
  location = "uksouth"
}
