import streamlit as st
from aiagent import generate_terraform_code, save_terraform_code, validate_and_fix, check_deployment_status
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

# Initialize Azure credentials and resource management client
credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, "b2e20b65-acfb-4c6c-b03c-e40cac5c3af7")

def run_app():
    st.title("Terraform AI Agent")
    
    # Get user input via a text field
    user_input = st.text_input("Enter the Azure infrastructure to create:")

    # Button to generate Terraform code
    if st.button("Generate Terraform Code"):
        if not user_input:
            st.warning("Please enter a valid infrastructure description.")
        else:
            with st.spinner("Generating Terraform code..."):
                terraform_code = generate_terraform_code(user_input)
            st.subheader("Generated Terraform Code:")
            st.code(terraform_code, language="hcl")
            
            # Button for user confirmation and to deploy the generated code
            if st.button("Confirm and Deploy"):
                with st.spinner("Saving Terraform code..."):
                    save_terraform_code(terraform_code)
                st.success("Terraform code saved to main.tf")
                
                with st.spinner("Validating and deploying..."):
                    validate_and_fix()
                    status = check_deployment_status()
                st.success(status)

if __name__ == '__main__':
    run_app()