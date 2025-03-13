import os
import re
import requests
import openai  # Use the openai module directly
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from dotenv import load_dotenv
import logging
import subprocess
import uuid
import streamlit as st  # Import Streamlit library
# Load environment variables from .env file
load_dotenv()
logging.basicConfig(filename='terraform.log', level=logging.INFO)
logging.info("Terraform deployment started.")

# Initialize Azure credentials and resource management client
credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, os.getenv("AZURE_SUBSCRIPTION_ID"))

# Configure OpenAI to use Azure OpenAI service
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g., "https://your-resource-name.openai.azure.com/"
openai.api_version = "2024-12-01-preview"  # Make sure this matches your deployment version
openai.api_key = os.getenv("AZURE_API_KEY")


def generate_terraform_code(user_input):
    prompt = f"Generate Terraform code for Azure to create: {user_input}. " \
             "Ensure the code lifecycle block has ignore_changes = [tags] and a tag Deploy_via = TerraformAIAgent to all resources." \
             "Generate as per the best practices and standards to use main.tf for resource creation and variables for variables.tf and and values for terraform.tfvars and mention the file names in the comments."    
                    
    response = openai.ChatCompletion.create(
        deployment_id="o3-mini",  # Update with your deployment id if different
        messages=[
            {"role": "system", "content": "You are a Terraform expert generating valid Azure Terraform code. Follow Terraform v1.0+ and AzureRM provider v3.0+ standards. Output only HCL code inside triple backticks (```hcl ... ```), without provider blocks, extra resources, or explanations.Ensure correctness per official guidelines (https://registry.terraform.io/providers/hashicorp/azurerm/latest) and validate for production readiness."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def make_unique_name(base_name):
    """Append a short unique suffix to the given base name."""
    unique_suffix = str(uuid.uuid4())[:8]
    return f"{base_name}-{unique_suffix}"


def generate_unique_terraform_code(user_input):
    """
    Generates Terraform code and handles duplicate resources
    """
    terraform_code = generate_terraform_code(user_input)
    output_file = "..\terraform\main.tf"
    existing_content = ""
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing_content = f.read()
    
    # Updated regex pattern to properly capture entire blocks including closing braces
    pattern = r'(resource\s+"([^"]+)"\s+"([^"]+)"\s*\{(?:[^{}]|(?:\{[^{}]*\}))*\})'
    blocks = re.findall(pattern, terraform_code, flags=re.DOTALL)
    modified_blocks = []
    
    for full_block, provider, ref_name, *_ in blocks:
        # Extract the name attribute from the block
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', full_block)
        code_name = name_match.group(1) if name_match else ref_name

        # Check for duplicates
        pattern_ref = rf'resource\s+"{provider}"\s+"{re.escape(ref_name)}"'
        pattern_name = rf'name\s*=\s*["\']{re.escape(code_name)}["\']'
        
        if re.search(pattern_ref, existing_content) or re.search(pattern_name, existing_content):
            new_ref_name = make_unique_name(ref_name)
            new_code_name = make_unique_name(code_name)
            
            # Update reference name and resource name
            new_block = re.sub(
                r'(resource\s+"'+provider+r'"\s+")'+re.escape(ref_name)+r'(")',
                r'\1'+new_ref_name+r'\2',
                full_block,
                count=1
            )
            new_block = re.sub(
                r'(name\s*=\s*["\'])'+re.escape(code_name)+r'(["\'])',
                r'\1'+new_code_name+r'\2',
                new_block,
                count=1
            )
            modified_blocks.append(new_block)
        else:
            modified_blocks.append(full_block)
    
    # Join blocks with proper spacing
    modified_code = "\n\n".join(modified_blocks)
    return modified_code
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

        
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr

def fix_terraform_code(error):
    # Use AI to fix errors
    response = openai.ChatCompletion.create(
        deployment_id="o3-mini",
        messages=[
            {"role": "system", "content": "Fix this Terraform error:"},
            {"role": "user", "content": error}
        ]
        # max_tokens=300
    )
    fixed = response.choices[0].message['content'].strip()
    print("Fixed code:", fixed)  # Debug print
    return fixed

def auto_commit_and_push():
    """
    Commits and pushes main.tf to the 'test' branch, then creates and auto-merges a pull request
    using GitHub CLI. Adjust the commands as needed for your workflow.
    """
    commit_message = "Auto-update Terraform configuration"
    stdout, stderr = run_command("git add main.tf")
    if stderr:
        logging.error(f"Git add error: {stderr}")
    stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if stderr:
        logging.error(f"Git commit error: {stderr}")
    stdout, stderr = run_command("git push -u origin test")
    if stderr:
        logging.error(f"Git push error: {stderr}")
    else:
        print("Committed and pushed updated code to 'test' branch.")

    # Create a pull request using GitHub CLI
    pr_create_cmd = (
        "gh pr create --title 'Auto PR for Terraform update' "
        "--body 'Automated PR generated by Terraform AI Agent' --base main --head test"
    )
    stdout, stderr = run_command(pr_create_cmd)
    if stderr:
        logging.error(f"GitHub PR creation error: {stderr}")
    else:
        print("Pull request created.")
    # Auto-merge the PR; adjust flags per your merge strategy
    pr_merge_cmd = "gh pr merge --squash --delete-branch --auto"
    stdout, stderr = run_command(pr_merge_cmd)
    if stderr:
        logging.error(f"GitHub PR merge error: {stderr}")
    else:
        print("Pull request merged and branch deleted.")

# Consolidated function to extract, verify, and merge code changes
def process_and_commit():
    """
    Extracts HCL code (if wrapped in triple backticks), saves it to main.tf,
    validates and fixes Terraform code (using terraform fmt, init, validate, & TFLint) once,
    and finally commits and merges the changes via GitHub CLI to trigger GitHub Actions.
    """
    # Extract HCL content from the modified code
    code = extract_hcl(st.session_state.modified_code)

    # Save the extracted code to main.tf
    output_file = "main.tf"
    with open(output_file, "a") as f:
        f.write("\n" + code + "\n")
    print("Appended HCL code to main.tf.")

    # Format and initialize Terraform
    run_command("terraform fmt")
    run_command("terraform init")

    # Validate Terraform syntax
    _, validate_err = run_command("terraform validate")
    if validate_err:
        logging.error(f"Validation Error: {validate_err}")
        fixed_code = fix_terraform_code(validate_err)
        with open(output_file, "w") as f:
            f.write(fixed_code)
        return "Validation error fixed. Please re-run the verification process."

    # Lint with TFLint
    _, tflint_err = run_command("tflint --chdir=.")
    if tflint_err:
        logging.error(f"Linting Error: {tflint_err}")
        fixed_code = fix_terraform_code(tflint_err)
        with open(output_file, "w") as f:
            f.write(fixed_code)
        return "Linting error fixed. Please re-run the verification process."

    # If all checks pass, commit, push, and merge the code
    auto_commit_and_push()
    return code

def verify_terraform_code():
    """
    Verifies the Terraform code without saving it to main.tf.
    Runs terraform formatting, initialization, validation, and linting.
    """
    # Extract HCL content from the modified code
    code = extract_hcl(st.session_state.modified_code)

    # Format and initialize Terraform
    run_command("terraform fmt")
    run_command("terraform init")

    # Validate Terraform syntax
    _, validate_err = run_command("terraform validate")
    if validate_err:
        logging.error(f"Validation Error: {validate_err}")
        fixed_code = fix_terraform_code(validate_err)
        return "Validation error fixed. Please re-run the verification process."

    # Lint with TFLint
    _, tflint_err = run_command("tflint --chdir=.")
    if tflint_err:
        logging.error(f"Linting Error: {tflint_err}")
        fixed_code = fix_terraform_code(tflint_err)
        return "Linting error fixed. Please re-run the verification process."

    return code

import os
import re
import os
import re

import os
import re

import os
import re

def save_and_deploy():
    """
    Appends the verified Terraform code dynamically into main.tf, variables.tf, and terraform.tfvars files
    under the ../terraform directory.
    """
    # Extract HCL content from the final code
    code = extract_hcl(st.session_state.final_code)
    
    # Define file paths outside src directory
    terraform_dir = "../terraform"
    os.makedirs(terraform_dir, exist_ok=True)
    
    # Use a more specific regex pattern to extract code blocks with their file markers
    # This pattern accounts for the exact format provided in the example
    code_blocks = re.split(r'```hcl', code)
    
    # Skip the first element which is likely empty or contains text before the first code block
    if code_blocks and not code_blocks[0].strip():
        code_blocks = code_blocks[1:]
    
    # Process each code block
    for block in code_blocks:
        if not block.strip():
            continue
            
        # Split at the end of the code block
        parts = block.split('```', 1)
        if len(parts) != 2:
            print(f"Warning: Malformed code block: {block[:50]}...")
            continue
            
        block_content = parts[0].strip()
        
        # Extract the filename from the first line (e.g., "// main.tf")
        lines = block_content.split('\n')
        if not lines:
            continue
            
        file_marker = lines[0].strip()
        if not file_marker.startswith('//'):
            print(f"Warning: Missing file marker, expected '// filename.tf', got: {file_marker}")
            continue
            
        filename = file_marker[2:].strip()  # Remove the '//' prefix and whitespace
        content_lines = lines[1:]  # Skip the first line which contains the filename
        content = '\n'.join(content_lines)
        
        # Save content to the appropriate file
        if filename in ["main.tf", "variables.tf", "terraform.tfvars"]:
            file_path = os.path.join(terraform_dir, filename)
            
            with open(file_path, "a") as f:
                f.write("\n" + content + "\n")
            
            print(f"Successfully appended content to {filename} in {terraform_dir}")
        else:
            print(f"Skipping unexpected file: {filename}")
    
    # Commit, push, and merge the code
    auto_commit_and_push()
    return code

def check_deployment_status():
    """
    Checks the status of the GitHub Actions deployment.
    Returns "Apply complete!" if terraform apply -autoapprove completed successfully,
    or an error message if the run failed or has issues.
    """
    try:
        # Run GitHub CLI command to get the latest action run status
        cmd = "gh run list --limit 1 --json status,conclusion,name"
        output, error = run_command(cmd)
        
        if error:
            return f"Deployment failed with error: {error}"
            
        import json
        runs = json.loads(output)
        
        if runs and len(runs) > 0:
            latest_run = runs[0]
            status = latest_run.get('status')
            conclusion = latest_run.get('conclusion')
            
            if status == "completed":
                if conclusion == "success":
                    # A successful run means terraform apply -autoapprove has finished successfully.
                    return "Apply complete!"
                else:
                    return f"Deployment failed with status: {conclusion}"
            else:
                return f"Deployment in progress: {status}"
        else:
            return "No deployment information found"
            
    except Exception as e:
        return f"Error checking deployment status: {str(e)}"

def main():
    try:
        user_input = input("Enter what Azure infrastructure to create (e.g., create a resource group name \"rg01\"): ")
        terraform_code = generate_terraform_code(user_input)
        print("\nGenerated Terraform Code:\n")
        print(terraform_code)
        process_and_commit(terraform_code)
        # process_and_commit()
    except Exception as e:
        print(f"An error occurred while generating Terraform code: {e}")
    except (EOFError, KeyboardInterrupt):
        print("\nInput interrupted. Exiting.")
        print(check_deployment_status())

if __name__ == '__main__':
    main()
