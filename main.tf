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
  name                = "rax_vnet01"
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
resource "azurerm_resource_group" "rg-aiagent01" {
  name     = "rg-aiagent01"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "rg_aiagent02" {
  name     = "rg-aiagent02"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "rg_aiagent03" {
  name     = "rg-aiagent03"
  location = "uksouth"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_resource_group" "rg_terraform" {
  name     = "rg-terraform"
  location = "uksouth"
}
resource "azurerm_resource_group" "rg_aiagent04" {
  name     = "rg-aiagent04"
  location = "uksouth"
}

resource "azurerm_resource_group" "anoop_aiproject01" {
  name     = "anoop_aiproject01"
  location = "uksouth"
}
resource "azurerm_resource_group" "rg-standard" {
  name     = "rg-standard"
  location = "uksouth"
}

resource "azurerm_virtual_network" "vnet-standard" {
  name                = "vnet-standard"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg-standard.location
  resource_group_name = azurerm_resource_group.rg-standard.name
}

resource "azurerm_subnet" "subnet-standard" {
  name                 = "subnet-standard"
  resource_group_name  = azurerm_resource_group.rg-standard.name
  virtual_network_name = azurerm_virtual_network.vnet-standard.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_security_group" "nsg-standard" {
  name                = "nsg-standard"
  location            = azurerm_resource_group.rg-standard.location
  resource_group_name = azurerm_resource_group.rg-standard.name

  security_rule {
    name                       = "Allow-RDP"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "subnet-nsg-assoc" {
  subnet_id                 = azurerm_subnet.subnet-standard.id
  network_security_group_id = azurerm_network_security_group.nsg-standard.id
}

resource "azurerm_public_ip" "pip-standard" {
  name                = "pip-standard"
  location            = azurerm_resource_group.rg-standard.location
  resource_group_name = azurerm_resource_group.rg-standard.name
  allocation_method   = "Dynamic"
  sku                 = "Basic"
}

resource "azurerm_network_interface" "nic-standard" {
  name                = "nic-standard"
  location            = azurerm_resource_group.rg-standard.location
  resource_group_name = azurerm_resource_group.rg-standard.name

  ip_configuration {
    name                          = "ipconfig-standard"
    subnet_id                     = azurerm_subnet.subnet-standard.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip-standard.id
  }
}

resource "azurerm_linux_virtual_machine" "vm-standard" {
  name                = "vm-standard"
  resource_group_name = azurerm_resource_group.rg-standard.name
  location            = azurerm_resource_group.rg-standard.location
  size                = "Standard_DS1_v2"
  admin_username      = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.nic-standard.id,
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-network01"
  location = "uksouth"
}

resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-network"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  address_space       = ["10.0.0.0/24"]
}

resource "azurerm_subnet" "subnet1-1146b2f2" {
  name                 = "subnet1-2eceb315"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.0.0/25"]
}

resource "azurerm_subnet" "subnet2-1ad245dd" {
  name                 = "subnet2-5b5adab7"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.0.128/25"]
}
