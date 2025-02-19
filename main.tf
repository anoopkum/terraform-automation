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
resource "azurerm_virtual_network" "anoop_vnet" {
  name                = "anoop_vnet"
  address_space       = ["10.0.0.0/16"]
  location            = "East US"
  resource_group_name = "anoopp_rg"
}

resource "azurerm_subnet" "anoop_subnet" {
  name                 = "anoop_subnet"
  resource_group_name  = "anoopp_rg"
  virtual_network_name = azurerm_virtual_network.anoop_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_interface" "anoop_nic" {
  name                = "anoop_nic"
  location            = "East US"
  resource_group_name = "anoopp_rg"

  ip_configuration {
    name                          = "anoop_ip_config"
    subnet_id                     = azurerm_subnet.anoop_subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_virtual_machine" "anoop_vm" {
  name                  = "anoop_vm"
  location              = "East US"
  resource_group_name   = "anoopp_rg"
  network_interface_ids = [azurerm_network_interface.anoop_nic.id]
  vm_size               = "Standard_DS2_v2" # 2 vCPUs, 8 GB RAM

  storage_os_disk {
    name          = "anoop_os_disk"
    caching       = "ReadWrite"
    create_option = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }

  os_profile {
    computer_name  = "anoopvm"
    admin_username = "adminuser"
    admin_password = "AdminPassword123!"
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }
}

resource "azurerm_network_security_group" "anoop_nsg" {
  name                = "anoop_nsg"
  location            = azurerm_resource_group.anoopp_rg.location
  resource_group_name = azurerm_resource_group.anoopp_rg.name
}
