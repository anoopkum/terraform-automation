terraform {
  required_version = ">= 1.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.00.0"
    }
  }
}


provider "azurerm" {
  features {}
}
resource "azurerm_resource_group" "anoopp_rg01" {
  name     = "anoopp-rg01"
  location = "uksouth"
}

resource "azurerm_resource_group" "anoopp_rg02" {
  name     = "anoopp-rg02"
  location = "uksouth"
}

resource "azurerm_resource_group" "anoopp_rg03" {
  name     = "anoopp-rg03"
  location = "uksouth"
}
resource "azurerm_resource_group" "anoopp_rg04" {
  name     = "anoopp-rg04"
  location = "uksouth"
}
resource "azurerm_resource_group" "anoopp_05" {
  name     = "anoopp-05"
  location = "uksouth"
}

resource "azurerm_resource_group" "example" {
  name     = "anoopp-06"
  location = "uksouth"
}
