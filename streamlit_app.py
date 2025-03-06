import streamlit as st
from dotenv import load_dotenv
import os
from aiagent import (
    generate_unique_terraform_code,
    verify_generated_code,
    validate_and_fix,
    save_terraform_code,
    check_deployment_status
)
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

# Initialize Azure credentials and Resource Management Client
credential = DefaultAzureCredential()
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")  # Replace with your subscription ID if different
resource_client = ResourceManagementClient(credential, subscription_id)

def run_app():
    st.title("Terraform AI Agent")
    
    # Initialize session state variables
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = ""
    if "modified_code" not in st.session_state:
        st.session_state.modified_code = ""
    if "final_code" not in st.session_state:
        st.session_state.final_code = ""
    
    # Get user input
    user_input = st.text_input(
        "Enter what Azure infrastructure to create (e.g. create a resource group name \"rg01\"):"
    )
    
    # Generate Code Section
    if st.button("Generate Terraform Code"):
        if user_input.strip() == "":
            st.error("Please enter a valid description.")
        else:
            with st.spinner("Generating Terraform code..."):
                code = generate_unique_terraform_code(user_input)
                st.session_state.generated_code = code
                st.session_state.modified_code = code
    
    # Show code editor (always visible after generation)
    if st.session_state.modified_code:
        st.subheader("Generated Terraform Code (Modify if required)")
        modified_code = st.text_area(
            "Terraform Code",
            value=st.session_state.modified_code,
            height=500,
            key="code_editor"
        )
        # Update the modified code in session state
        st.session_state.modified_code = modified_code
        
        # Verify Code Section
        st.subheader("Verify Terraform Code")
        if st.button("Verify Terraform Code"):
            with st.spinner("Verifying code..."):
                verification_result = verify_generated_code(st.session_state.modified_code)
            
            if verification_result.startswith(("Formatting error", "Terraform init error", "Validation error", "TFLint error")):
                st.error(verification_result)
            else:
                st.success("Terraform code verified successfully.")
                st.session_state.final_code = verification_result
                st.subheader("Final Verified Terraform Code")
                st.text_area(
                    "Final Terraform Code",
                    value=verification_result,
                    height=500,
                    key="final_code_viewer"
                )
        
        # Deploy Section
        if st.session_state.final_code:
            st.subheader("Save and Deploy")
            if st.button("Save and Deploy"):
                with st.spinner("Saving code and triggering deployment..."):
                    save_terraform_code(st.session_state.final_code)
                    st.success("Terraform code saved to main.tf. Deployment in progress...")
                # Add deployment status checking
                with st.spinner("Checking deployment status..."):
                    deployment_status = check_deployment_status()
                    if "Deployment failed" in deployment_status:
                        st.error(deployment_status)
                    elif "Deployment successful" in deployment_status:
                        st.success(deployment_status)
                    else:
                        st.warning("Deployment status unknown. Please check GitHub Actions.")
if __name__ == "__main__":
    run_app()