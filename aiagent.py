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
             "Output ONLY the HCL code wrapped in triple backticks with 'hcl' as the language (NO instructions)."
             
    response = openai.ChatCompletion.create(
        deployment_id="o3-mini",  # Update with your deployment id if different
        messages=[
            {"role": "system", "content": "You are a Terraform expert generating valid Azure Terraform code. Follow Terraform v1.0+ and AzureRM provider v3.0+ standards. Output only HCL code inside triple backticks (```hcl ... ```), without provider blocks, extra resources, or explanations. Adhere to the official guidelines: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs."},
            {"role": "user", "content": prompt}
        ]
        # max_tokens=500
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
    output_file = "main.tf"
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

def verify_generated_code(code):
    """
    Verifies the generated Terraform code using terraform fmt and basic validation
    """
    import os
    import tempfile
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "main.tf")
    
    try:
        # Write the code to a temporary .tf file
        with open(temp_file, "w") as f:
            f.write(code)
        
        # Run terraform fmt
        fmt_out, fmt_err = run_command(f"terraform fmt {temp_file}")
        if fmt_err:
            return f"Formatting error: {fmt_err}"
        
        # Basic syntax validation (doesn't require init)
        validate_out, validate_err = run_command(f"terraform validate -json {temp_file}")
        if validate_err:
            return f"Validation error: {validate_err}"
        
        # Run TFLint (doesn't require terraform init)
        tflint_out, tflint_err = run_command(f"cd {temp_dir} && tflint")
        if tflint_err:
            return f"TFLint error: {tflint_err}"
        
        # Read the formatted code
        with open(temp_file, "r") as f:
            final_code = f.read()
        
        return final_code
        
    finally:
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
def save_terraform_code(code):
    """
    Extracts HCL block (if wrapped in ```hcl ... ```) and saves it to main.tf.
    """
    hcl_code = code
    pattern = r"```hcl\s*(.*?)\s*```"
    match = re.search(pattern, code, re.DOTALL)
    if match:
        hcl_code = match.group(1)
    output_file = "main.tf"
    current_content = ""
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            current_content = f.read()
    new_content = current_content + "\n" + hcl_code + "\n"
    with open(output_file, "w") as f:
        f.write(new_content)
    print("Appended HCL code and updated main.tf.")

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
    fixed = response.choices[0].message.content.strip()
    print("Fixed code:", fixed)  # Debug print
    return fixed

def auto_commit_and_push():
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
        print("Committed and pushed updated code to test branch.")

def validate_and_fix():
        # Format the code with terraform fmt
    run_command("terraform fmt")
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
    auto_commit_and_push()

def check_deployment_status():
    """
    Checks the status of the GitHub Actions deployment
    Returns a message indicating success or failure with details
    """
    try:
        # Run git command to get the latest action run status
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
                    return "Deployment successful"
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
        user_input = input("Enter what Azure infrastructure to create (e.g., create a resource group name \"anoop-rg000001\"): ")
        terraform_code = generate_unique_terraform_code(user_input)
        print("\nGenerated Terraform Code:\n")
        print(terraform_code)
        save_terraform_code(terraform_code)
        validate_and_fix()
    except Exception as e:
        print(f"An error occurred while generating Terraform code: {e}")
    except (EOFError, KeyboardInterrupt):
        print("\nInput interrupted. Exiting.")
        print(check_deployment_status())

if __name__ == '__main__':
    main()
