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

lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoopp_rg01" {
  name     = "anoopp-rg01"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoopp_rxt02" {
  name     = "anoopp-rxt02"
  location = "East US"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_virtual_network" "rax_vnet" {
  name                = "rax_vnet"
  address_space       = ["10.1.0.0/24"]
  location            = "East US"
  resource_group_name = "anoopp-rg01"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_subnet" "subnet1" {
  name                 = "subnet1"
  resource_group_name  = "anoopp-rg01"
  virtual_network_name = azurerm_virtual_network.rax_vnet.name
  address_prefixes     = ["10.1.0.0/26"]
}

resource "azurerm_subnet" "subnet2" {
  name                 = "subnet2"
  resource_group_name  = "anoopp-rg01"
  virtual_network_name = azurerm_virtual_network.rax_vnet.name
  address_prefixes     = ["10.1.0.64/26"]
}

resource "azurerm_resource_group" "anoopp_rg03" {
  name     = "anoopp-rg03"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoopp_rg04" {
  name     = "anoopp-rg04"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoopp_rg05" {
  name     = "anoopp-rg05"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoopp_rg06" {
  name     = "anoopp-rg06"
  location = "uksouth"
  tags = {
    "Deployed via" = "Terraform AI Agent"
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoopp_rg07" {
  name     = "anoopp-rg07"
  location = "uksouth"
  tags = {
    "Deployed via" = "Terraform AI Agent"
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoopp_rg10" {
  name     = "anoopp-rg10"
  location = "uksouth"
  tags = {
    "Deployed via" = "Terraform AI Agent"
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoopp_rg11" {
  name     = "anoopp-rg11"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoop_rg0001" {
  name     = "anoop-rg0001"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "anoop_rg" {
  name     = "anoop-rg000001"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}
resource "azurerm_resource_group" "anoop_rg000001" {
  name     = "anoop-rg000001"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}
