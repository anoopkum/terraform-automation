import os
import re
import requests
import openai
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from dotenv import load_dotenv
import logging
import subprocess
# Load environment variables from .env file
load_dotenv()

logging.basicConfig(filename='terraform.log', level=logging.INFO)
logging.info("Terraform deployment started.")

# Initialize Azure credentials and resource management client
credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, "b2e20b65-acfb-4c6c-b03c-e40cac5c3af7")

# Configure OpenAI to use Azure OpenAI service
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g., "https://your-resource-name.openai.azure.com/"
openai.api_version = "2024-08-01-preview"             # Must match your resource version
openai.api_key = os.getenv("AZURE_API_KEY")

def generate_terraform_code(user_input):
    prompt = f"Generate Terraform code for Azure to create: {user_input}" \
             "Output ONLY the HCL code wrapped in triple backticks with 'hcl' as the language (NO instructions)."
    response = openai.ChatCompletion.create(
    deployment_id="gpt-4",  # Use your deployment name if it's different
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates Terraform code for Azure as per user query, do not include any provider, additional resources or instructions. You also need to ensure the generated code is valid and can be deployed. please also add adding a lifecycle block with ignore_changes = [tags] to all resources."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def extract_hcl(content):
    """
    Extracts only the HCL content between ```hcl and ``` markers.
    If no such block is found, returns the original content.
    """
    pattern = r"```hcl\s*(.*?)\s*```"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return content

def get_latest_azurerm_version():
    """
    Queries the Terraform Registry for the latest stable version of the azurerm provider.
    Returns the version as a string. Falls back to "3.0.0" if lookup fails.
    """
    url = "https://registry.terraform.io/v1/providers/hashicorp/azurerm/versions"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            versions = []
            for v in data.get("versions", []):
                version = v.get("version")
                # Include only stable releases (only digits and dots)
                if re.match(r"^\d+(\.\d+)+$", version):
                    versions.append(version)
            if versions:
                versions.sort(key=lambda s: tuple(map(int, s.split('.'))))
                return versions[-1]
    except Exception as e:
        print(f"An error occurred while fetching provider version: {e}")
    return "3.0.0"  # Fallback version

def save_terraform_code(code):
    # Extract only the HCL content from the generated code.
    hcl_code = extract_hcl(code)
    # Prepare a terraform block with required version and provider settings.
    latest_version = get_latest_azurerm_version()
    tf_requirements = f'''terraform {{
  required_version = ">= 1.0.0"
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> {latest_version}"
    }}
  }}
}}

'''
    output_file = "main.tf"
    current_content = ""
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            current_content = f.read()
    # If the terraform block is not present, prepend it.
    if "terraform {" not in current_content:
        new_content = tf_requirements + current_content
    else:
        new_content = current_content
    # Append the new HCL code (separated by newlines)
    new_content += "\n" + hcl_code + "\n"
    with open(output_file, "w") as f:
        f.write(new_content)
    print("Appended HCL code and updated required terraform/provider version in main.tf")



def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr

def fix_terraform_code(error):
    # Use AI to fix errors
    response = openai.ChatCompletion.create(
        deployment_id="gpt-4",
        messages=[
            {"role": "system", "content": "Fix this Terraform error:"},
            {"role": "user", "content": error}
        ]
    )
    fixed = response.choices[0].message.content.strip()
    print("Fixed code:", fixed)  # Debug print
    return fixed

def auto_commit_and_push():
    commit_message = "Auto-update Terraform configuration"
    # Add the file, commit, and push to the main branch
    stdout, stderr = run_command("git add main.tf")
    if stderr:
        logging.error(f"Git add error: {stderr}")
    stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if stderr:
        logging.error(f"Git commit error: {stderr}")
    stdout, stderr = run_command("git push --force origin test")
    if stderr:
        logging.error(f"Git push error: {stderr}")
    else:
        print("Committed and pushed updated code to test branch.")

def validate_and_fix():
    # Initialize Terraform
    run_command("terraform init")
    
    # Validate syntax
    _, validate_err = run_command("terraform validate")
    if validate_err:
        logging.error(f"Validation Error: {validate_err}")
        fixed_code = fix_terraform_code(validate_err)
        save_terraform_code(fixed_code)
        validate_and_fix()  # Recursive retry
    
    # Lint with TFLint
    _, tflint_err = run_command("tflint --chdir=.")
    if tflint_err:
        logging.error(f"Linting Error: {tflint_err}")
        fixed_code = fix_terraform_code(tflint_err)
        save_terraform_code(fixed_code)
        validate_and_fix()
    
    # If validations pass, auto commit and push changes
    auto_commit_and_push()

def check_deployment_status():
    """
    Checks the status of the latest GitHub Actions workflow run for deployment.
    Returns “Deployment successful” if the run concluded with success,
    or a message indicating the failure status.
    """
    # Replace with your actual repository in the format "owner/repo"
    repo = "anoopkum/terraform-automation"
    
    # Build headers for authentication using your GITHUB_TOKEN
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Deployment status unknown: Missing GITHUB_TOKEN"
    headers = {"Authorization": f"token {token}"}
    
    # Query GitHub Actions to get the list of workflow runs
    runs_url = f"https://api.github.com/repos/{repo}/actions/runs"
    response = requests.get(runs_url, headers=headers)
    
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        if not runs:
            return "Deployment status unknown: No workflow runs found"
        # Assume the most recent workflow run is our deployment job
        latest_run = runs[0]
        conclusion = latest_run.get("conclusion")
        if conclusion == "success":
            return "Deployment successful"
        else:
            return f"Deployment failed with status: {conclusion}"
    else:
        return f"Failed to fetch deployment status (HTTP {response.status_code})"

def main():
    try:
        user_input = input("Enter what Azure infrastructure to create: ")
        terraform_code = generate_terraform_code(user_input)
        print("\nGenerated Terraform Code:\n")
        print(terraform_code)
        save_terraform_code(terraform_code)
        # Trigger validation after code is updated.
        validate_and_fix()
    except Exception as e:
        print(f"An error occurred while generating Terraform code: {e}")
    except (EOFError, KeyboardInterrupt):
        print("\nInput interrupted. Exiting.")
        print(check_deployment_status())

if __name__ == '__main__':
    main()