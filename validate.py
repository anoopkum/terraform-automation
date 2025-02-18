import os
import subprocess
import logging
from openai import AzureOpenAI
from aiagent import save_terraform_code

logging.basicConfig(level=logging.INFO)

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_API_KEY"),
    azure_endpoint="https://ai-aihub01771178575364.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-08-01-preview",  # Replace with your OpenAI endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  # e.g., "https://<your-resource-name>.openai.azure.com/"
    api_version="2024-08-01-preview"
)

def fix_terraform_code(error):
    # Use AI to fix errors
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Fix this Terraform error:"},
            {"role": "user", "content": error}
        ]
    )
    return response.choices[0].message.content

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
    _, tflint_err = run_command("tflint")
    if tflint_err:
        logging.error(f"Linting Error: {tflint_err}")
        fixed_code = fix_terraform_code(tflint_err)
        save_terraform_code(fixed_code)
        validate_and_fix()

    if __name__ == "__main__":
        validate_and_fix()