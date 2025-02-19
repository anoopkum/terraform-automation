terraform {
  required_version = ">= 1.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.19.0"
    }
  }
}


provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "anoopp_rg" {
  name     = "anoopp-rg"
  location = "uksouth"
}

resource "azurerm_virtual_network" "my_vnet" {
       name                = "myVnet"
       address_space       = ["10.0.0.0/16"]
       location            = "East US"
       resource_group_name = "myResourceGroup"
     }