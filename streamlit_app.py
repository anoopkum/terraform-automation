import streamlit as st
from aiagent import generate_terraform_code, save_terraform_code, validate_and_fix, check_deployment_status

def run_app():
    st.title("Terraform AI Agent")
    
    # Get user input via a text field
    user_input = st.text_input("Enter the Azure infrastructure to create:")
    
    if st.button("Generate & Deploy"):
        if not user_input:
            st.warning("Please enter a valid infrastructure description.")
        else:
            # Generate Terraform HCL code
            with st.spinner("Generating Terraform code..."):
                terraform_code = generate_terraform_code(user_input)
            st.subheader("Generated Terraform Code:")
            st.code(terraform_code, language="hcl")
            
            # Save the generated code to main.tf
            with st.spinner("Saving Terraform code..."):
                save_terraform_code(terraform_code)
            st.success("Terraform code saved to main.tf")
            
            # Run validations, linting, and deployment steps
            with st.spinner("Validating and deploying..."):
                validate_and_fix()
                status = check_deployment_status()
            st.success(status)

if __name__ == '__main__':
    run_app()