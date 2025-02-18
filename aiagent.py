import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from openai import AzureOpenAI

# Initialize Azure credentials and resource management client
credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, "b2e20b65-acfb-4c6c-b03c-e40cac5c3af7")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_API_KEY"),
    azure_endpoint="https://ai-aihub01771178575364.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-08-01-preview",  # Replace with your OpenAI endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  # e.g., "https://<your-resource-name>.openai.azure.com/"
    api_version="2024-08-01-preview"
)

# Function to generate Terraform code using OpenAI
def generate_terraform_code(user_input):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant that generates Terraform code for Azure."},
        {"role": "user", "content": user_input}
    ]
    response = client.chat.completions.create( # Replace with your deployment name
        model="gpt-4",
        messages=conversation
    )
    return response.choices[0].message.content.strip()

def save_terraform_code(code):
    with open("main.tf", "w") as f:
        f.write(code)
    print("Saved Terraform code to main.tf")

def check_deployment_status():
    # Query Azure for resource status
    # Implement API calls to check deployment
    ok = True # Placeholder for deployment status
    return "Deployment successful" if ok else "Failed: Resource conflict"

# Main function
def main():
    try:
        user_input = input("Enter what Azure infrastructure to create: ")
        terraform_code = generate_terraform_code(user_input)
        print("\nGenerated Terraform Code:\n")
        print(terraform_code)
    except Exception as e:
        print(f"An error occurred while generating Terraform code: {e}")
    except (EOFError, KeyboardInterrupt):
        print("\nInput interrupted. Exiting the program.")
        save_terraform_code(terraform_code) # Save the generated Terraform code to a main.tf file
        print(check_deployment_status())

if __name__ == '__main__':
    main()