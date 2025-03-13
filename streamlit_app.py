import streamlit as st
from aiagent import (
    generate_terraform_code,
    verify_terraform_code,
    save_and_deploy,
    check_deployment_status
)

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
    user_input = st.text_area(
        "Enter what Azure infrastructure to create (e.g. create a resource group name \"rg01\"):",
        height=100
    )
    
    # Generate Code Section
    if st.button("Generate Terraform Code"):
        if user_input.strip() == "":
            st.error("Please enter a valid description.")
        else:
            with st.spinner("Generating Terraform code..."):
                code = generate_terraform_code(user_input)
                st.session_state.generated_code = code
                st.session_state.modified_code = code
    
    # Show code editor (always visible after generation)
    if st.session_state.modified_code:
        st.subheader("Generated Terraform Code (Modify if required)")
        modified_code_length = len(st.session_state.modified_code.split("\n"))  # Count lines instead of characters
        dynamic_height = min(800, max(100, modified_code_length * 20))  # Adjust height based on lines

        modified_code = st.text_area(
        "Terraform Code",
        value=st.session_state.modified_code,
        height=dynamic_height,
        key="code_editor"
        )
        # Update the modified code in session state
        st.session_state.modified_code = modified_code
        
        # Verify Code Section
        st.subheader("Verify Terraform Code")
        if st.button("Verify Terraform Code"):
            with st.spinner("Verifying code..."):
                verification_result = verify_terraform_code()
            
            if verification_result and verification_result.startswith(("Validation error", "Linting error")):
                st.error(verification_result)
            else:
                st.success("Terraform code verified successfully.")
                st.session_state.final_code = verification_result
                st.subheader("Final Verified Terraform Code")
                st.code(
                    verification_result,
                    language="hcl"  # Use HCL for Terraform syntax highlighting
                )
        
        # Deploy Section
        if st.session_state.final_code:
            st.subheader("Save and Deploy")
            if st.button("Save and Deploy"):
                with st.spinner("Triggering deployment..."):
                    save_and_deploy()
                    st.success("Deployment triggered!")
                
                # Display deployment status until a final outcome is reached
                status_placeholder = st.empty()
                status_placeholder.info("Deployment is in progress. Please wait...")

                with st.spinner("Checking deployment status..."):
                    while True:
                        deployment_status = check_deployment_status()
                        status_lower = deployment_status.lower()
                        if "apply complete!" in status_lower:
                            status_placeholder.success("Deployment Successful!")
                            break
                        elif "error:" in status_lower:
                            status_placeholder.error(f"Deployment Failed: {deployment_status}")
                            break
                        else:
                            status_placeholder.info("Deployment is in progress. Please wait...")

if __name__ == "__main__":
    run_app()