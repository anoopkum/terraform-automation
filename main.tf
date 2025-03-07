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
    storage_account_name = "saterraformstaterxt" # Replace with your Azure storage account name
    container_name       = "terraformstate"      # Replace with your container name if different
    key                  = "terraform.tfstate"   # The state file name
  }
}
provider "azurerm" {
  features {}
}

data "azurerm_key_vault" "azure_kv" {
  name                = "raxtfkvtf" # Replace with your Key Vault name
  resource_group_name = "raxtfrgtf" # Replace with your resource group
}

resource "azurerm_resource_group" "anoopp_rg01" {
  name     = "anoopp-rg01"
  location = "uksouth"

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
    name                       = "Allow-SSH"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
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

resource "random_password" "vm_password" {
  length           = 16
  special          = true
  override_special = "!@#$%^&*()"
}

resource "azurerm_key_vault_secret" "vm_password_secret" {
  name         = "vm-password"                      # Name of the secret in Key Vault
  value        = random_password.vm_password.result # Use generated password
  key_vault_id = data.azurerm_key_vault.azure_kv.id
}

data "azurerm_key_vault_secret" "vm_password_secret" {
  name         = "vm-password" # Name of the secret in Key Vault
  key_vault_id = data.azurerm_key_vault.azure_kv.id

  depends_on = [azurerm_key_vault_secret.vm_password_secret]
}



resource "azurerm_linux_virtual_machine" "vm-standard" {
  name                            = "vm-standard"
  resource_group_name             = azurerm_resource_group.rg-standard.name
  location                        = azurerm_resource_group.rg-standard.location
  size                            = "Standard_B2ms"
  admin_username                  = "azureuser"
  admin_password                  = data.azurerm_key_vault_secret.vm_password_secret.value # Retrieve stored password
  disable_password_authentication = false

  network_interface_ids = [
    azurerm_network_interface.nic-standard.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }
}
resource "azurerm_resource_group" "rg_test" {
  name     = "rg-test0001"
  location = "uksouth"
}

# resource "azurerm_resource_group" "rg_test" {
#   name     = "rg-test0001"
#   location = "uksouth"
# }

resource "azurerm_resource_group" "akash_rg001" {
  name     = "akash-rg001"
  location = "uksouth"
}

resource "azurerm_resource_group" "akash_rg002" {
  name     = "akash-rg002"
  location = "uksouth"
}
resource "azurerm_resource_group" "akash_005" {
  name     = "akash-005"
  location = "uksouth"
}
