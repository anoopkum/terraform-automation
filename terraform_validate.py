# import subprocess
# import requests
# import re

# def run_terraform_command(command):
#     result = subprocess.run(command, shell=True, capture_output=True, text=True)
#     return result.stdout, result.stderr

# def get_latest_azurerm_version():
#     url = "https://registry.terraform.io/v1/providers/hashicorp/azurerm/versions"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         versions = []
#         # Loop through available versions and select only stable (non-prerelease) versions.
#         for v in data.get("versions", []):
#             version = v.get("version")
#             # Ignore pre-release versions if any (they contain letters, e.g. "rc")
#             if re.match(r"^\d+(\.\d+)+$", version):
#                 versions.append(version)
#         if versions:
#             # Sort versions using tuple comparison on numeric parts
#             versions.sort(key=lambda s: tuple(map(int, s.split('.'))))
#             return versions[-1]  # Return the latest version
#     return ">= 3.0.0"  # Fallback version if request fails

# def ensure_terraform_requirements(file_path="main.tf"):
#     with open(file_path, "r+") as tf_file:
#         content = tf_file.read()
#         # Check if a terraform block already exists
#         if "terraform {" not in content:
#             latest_version = get_latest_azurerm_version()
#             # Prepare the terraform block with required_version and required_providers settings
#             tf_requirements = f'''terraform {{
#   required_version = ">= 1.0.0"
#   required_providers {{
#     azurerm = {{
#       source  = "hashicorp/azurerm"
#       version = "~> {latest_version}"
#     }}
#   }}
# }}

# '''
#             updated_content = tf_requirements + content
#             tf_file.seek(0)
#             tf_file.write(updated_content)
#             tf_file.truncate()
#             print("Terraform requirements block added to main.tf")
#         else:
#             print("Terraform requirements block already exists in main.tf")

# # Your generated Terraform configuration (without a terraform block)
# terraform_configuration = """
# provider "azurerm" {
#   features {}
# }

# resource "azurerm_resource_group" "rg" {
#   name     = "rsourceGroupsExample"
#   location = "East US"
# }

# resource "azurerm_virtual_network" "vnet" {
#   name                = "vnetExample"
#   address_space       = ["10.0.0.0/16"]
#   location            = azurerm_resource_group.rg.location
#   resource_group_name = azurerm_resource_group.rg.name
# }

# resource "azurerm_subnet" "subnet1" {
#   name                 = "subnet1Example"
#   resource_group_name  = azurerm_resource_group.rg.name
#   virtual_network_name = azurerm_virtual_network.vnet.name
#   address_prefixes     = ["10.0.1.0/24"]
# }

# resource "azurerm_subnet" "subnet2" {
#   name                 = "subnet2Example"
#   resource_group_name  = azurerm_resource_group.rg.name
#   virtual_network_name = azurerm_virtual_network.vnet.name
#   address_prefixes     = ["10.0.2.0/24"]
# }
# """

# # Write the generated configuration to main.tf
# with open("main.tf", "w") as tf_file:
#     tf_file.write(terraform_configuration)

# print("Terraform configuration has been written to main.tf")

# # Automatically fix missing terraform requirements by ensuring the necessary block is in place.
# ensure_terraform_requirements("main.tf")

# # Run Terraform commands
# stdout, stderr = run_terraform_command("terraform init")
# print("Terraform init output:")
# print(stdout)
# if stderr:
#     print("Terraform init errors:")
#     print(stderr)

# stdout, stderr = run_terraform_command("terraform validate")
# print("Terraform validate output:")
# print(stdout)
# if stderr:
#     print("Terraform validate errors:")
#     print(stderr)

# # Run TFLint for additional static analysis and validation
# stdout, stderr = run_terraform_command("tflint")
# print("TFLint output:")
# print(stdout)
# if stderr:
#     print("TFLint errors:")
#     print(stderr)