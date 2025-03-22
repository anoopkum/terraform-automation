# **How Terraform AI Agent Works?**  

With just **three simple clicks**, you can generate and deploy fully validated Terraform infrastructure in **Azure**.  

## 🔹 **Step 1: Enter Infrastructure Request**  
No more writing Terraform code manually!  
✅ Simply enter your infrastructure request in the **User prompt**.  
✅ Example: `"Create a resource group named aiagent-terraform-rg in uksouth."`  
✅ AI instantly **generates Terraform code** and **checks existing infrastructure** to avoid duplicate resources.  
✅ **Supports custom modules & templates** to meet compliance needs and eliminate **AI hallucinations** (incorrect code).  

---

## 🔹 **Step 2: Validate & Auto-Fix Code**  
Before deployment, the AI ensures the code is **error-free** and follows **Terraform best practices**:  
✅ Runs `terraform fmt` to format the code.  
✅ Uses `terraform validate` to check syntax correctness.  
✅ Applies `TFLint` to detect security misconfigurations.  
✅ If errors are found, **AI auto-fixes them** to ensure compliance.  

---

## 🔹 **Step 3: Deploy via GitHub Actions**  
Now comes the **magic of full automation!**  
✅ Click **"Save & Deploy"**, and the **verified Terraform code** is automatically **pushed to GitHub**.  
✅ This triggers **GitHub Actions**, which runs:  
🔹 `terraform init`  
🔹 `terraform validate`  
🔹 `terraform plan`  
🔹 `terraform apply`  

---

🌍 **Once the apply is complete:**  
✅ The **requested infrastructure is deployed in Azure**.  
✅ The **Terraform state is securely stored in Azure Blob Storage**.  
