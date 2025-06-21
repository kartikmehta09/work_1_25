# %%
'doc_1/doc_master_1'

'/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/doc_master_1'

# %%
import os
import sys
import ast
#import boto3
import json
import re

# %%
# Constants
REPO_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/doc_master_1'
OUTPUT_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/doc_master_1/output_path'

# Signature for generated documentation
SIGNATURE = """# Auto-generated Documentation

This documentation was automatically generated using a Large Language Model.

"""

# %%

# System prompts for the LLM
BASIC_DOCS_SYSTEM_PROMPT = """Your job is to act as the expert software engineer and provide detailed technical documentation broken into readable formats. 
You will be able to read the majority of a code repository given as a converted single text with the Prefix "#File:" declaring the start of the new file e.g., # File: masters-and-sons-main/src/components/ArrowTable.tsx. 
Typescript projects are required to use pnpm for commands, python project if they have a pyproject.toml will be using poetry. MySQL databases are typically planetscale, and in that case we follow planetscales recommended use of prisma (if prisms ORM is used).
Documentation should be broken down into:
Introduction:
- Provide a brief overview of the project.
- Mention the purpose and core functionality of the code repository.
- Highlight the key features and potential use cases.
Codebase Overview:
- Provide an in-depth overview of the codebase architecture and design patterns used.
- Detail the modules, components, and their interactions within the application.
Development Environment Setup:
- Step-by-step instructions for setting up the development environment, including necessary tools and dependencies.
- Include guidelines for configuring IDEs, linters, and other development tools.
Code Repository Structure:
- Explain the repository structure, detailing the purpose of different directories and files.
- Document naming conventions, file organization, and any specific standards followed in the codebase.
Key Points of Complexity:
- Outline each keypoint of complexity
    - Breakdown each keypoint
Installation and Setup:
- Offer detailed instructions on installing and setting up the project.
- Include any prerequisites or dependencies required.
Getting Started:
- Guide users through a simple, initial setup or quick-start process.
- Include basic examples or a simple tutorial to help users begin using the project quickly.
The output should be detailed in standard markdown, using headers to improve readability.
"""

REFINED_DOCS_FOLLOW_UP_PROMPT = """You are instructed to further refine the documentation, there is no need to repeat basic content. Focus on delivering expert value insights for internal development handover outlined in the below criteria.
In-Depth Architecture Overview:
- Provide comprehensive diagrams and descriptions of the system architecture, including data flow, service interactions, and external dependencies.
- Detail the critical architectural decisions and their justifications, discussing the trade-offs and alternatives considered.
Advanced Codebase Insights:
- Delve into complex modules and components, explaining intricate details that are crucial for understanding system behavior.
- Document any non-obvious implementation strategies and optimizations, explaining why they were necessary and how they impact the system.
Environment and Toolchain Deep Dive:
- Offer a detailed guide on the development, testing, and production environments, including specific configurations, underlying infrastructure details, and environment parity practices.
- Describe the complete toolchain, including build systems, deployment pipelines, and any custom tooling.
Critical Dependency Analysis:
- Provide an exhaustive overview of external libraries, frameworks, and services the system depends on, including versioning, patching strategies, and known issues.
- Discuss how dependencies are managed, potential risks associated with them, and mitigation strategies.
Performance Considerations:
- Document performance benchmarks, profiling methods, and optimization strategies.
- Include case studies of past performance issues, their analysis, and the solutions implemented.
Security Protocols:
- Detail the security measures and protocols in place, including authentication, authorization, data encryption, and any proprietary security frameworks or libraries.
- Discuss security best practices, known vulnerabilities (and their mitigations), and any relevant security audits.
Testing and Quality Assurance:
- Elaborate on the testing strategy, including unit, integration, and end-to-end tests, highlighting any test-driven development (TDD) practices.
- Document the approach to continuous integration/continuous deployment (CI/CD), test automation, and quality benchmarks.
Troubleshooting and Debugging Guide:
- Provide a detailed guide for troubleshooting common issues, including debugging tips, logging best practices, and monitoring tools used.
- Share real-world incidents or outages, post-mortem analyses, and lessons learned.
Data Management and Migration:
- Explain the data architecture, schema design, and any data migration strategies or scripts.
- Discuss backup strategies, data integrity checks, and disaster recovery plans.
Developer Onboarding:
- Create a comprehensive onboarding guide for new developers, including step-by-step setup instructions, key contacts, and resources for getting up to speed.
- Include a glossary of terms, acronyms, and jargon used within the project to aid in understanding the documentation and codebase.
"""


# %%
# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List of file extensions to include
code_extensions = [
    ".py", ".ipynb", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h", 
    ".go", ".rs", ".php", ".rb", ".cs", ".sh", ".html", ".css", ".scss"
]

# List of directories and file patterns to exclude
excluded_dirs = [
    "docs",
    "examples",
    "tests",
    "test",
    "__pycache__",
    "scripts",
    "benchmarks",
    "node_modules",
    ".venv",
]
utility_or_config_files = ["hubconf.py", "setup.py", "package-lock.json"]
github_workflow_or_docs = ["stale.py", "gen-card-", "write_model_card"]


# %%
# Extract code from repository
print(f"Extracting code from {REPO_DIR}...")
repo_name = os.path.basename(REPO_DIR)
output_file = os.path.join(OUTPUT_DIR, f"{repo_name}_code.txt")

# %%
repo_name

# %%
output_file

# %%
# Extract code from repository
print(f"Extracting code from {REPO_DIR}...")
repo_name = os.path.basename(REPO_DIR)
output_file = os.path.join(OUTPUT_DIR, f"{repo_name}_code.txt")

# Open the output file for writing
with open(output_file, "w", encoding="utf-8") as outfile:
    # Walk through the repository directory
    for root, _, files in os.walk(REPO_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip if file path ends with "/"
            if file_path.endswith("/"):
                continue
            
            # Check if file has a desired extension
            if not any(file_path.endswith(ext) for ext in code_extensions):
                continue
            
            # Check if file is in excluded directory
            check_path = file_path.replace("\\", "/")
            parts = check_path.split(os.sep)[1:]
            if any(part.startswith(".") for part in parts):
                continue
            
            if "test" in check_path.lower():
                continue
                
            skip_file = False
            for excluded_dir in excluded_dirs:
                if f"/{excluded_dir}/" in check_path or check_path.startswith(f"{excluded_dir}/"):
                    skip_file = True
                    break
                    
            if skip_file:
                continue
                
            for file_name in utility_or_config_files:
                if file_name in check_path:
                    skip_file = True
                    break
                    
            if skip_file:
                continue
                
            if not all(doc_file not in check_path for doc_file in github_workflow_or_docs):
                continue
            
            # Try to read the file
            try:
                with open(file_path, "r", encoding="utf-8") as file_content:
                    # Skip files with insufficient substantive content
                    file_lines = file_content.readlines()
                    lines = [
                        line
                        for line in file_lines
                        if line.strip() and not line.strip().startswith("//")
                    ]
                    
                    if len(lines) < 5:  # Skip files with less than 5 substantive lines
                        continue
                        
                    # Write file path and content to output file
                    outfile.write(f"# File: {file_path}\n")
                    
                    # For Python files, try to clean comments and docstrings
                    if file_path.endswith(".py"):
                        try:
                            source = "".join(file_lines)
                            tree = ast.parse(source)
                            for node in ast.walk(tree):
                                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and ast.get_docstring(node):
                                    node.body = node.body[1:]  # Remove docstring
                                elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                                    node.value.s = ""  # Remove comments
                            cleaned_source = ast.unparse(tree)
                            outfile.write(cleaned_source)
                        except:
                            # If ast parsing fails, write the original source
                            outfile.writelines(file_lines)
                    else:
                        # For non-Python files, write original content
                        outfile.writelines(file_lines)
                        
                    outfile.write("\n\n")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

print(f"Code extracted to {output_file}")

# %%
# Estimate token size
with open(output_file, "r", encoding="utf-8") as file:
    repo_content = file.read()
    # Very simple estimation - approximately 4 characters per token
    token_size = len(repo_content) // 4
    print(f"Input token size estimate: {token_size}")

# %%
# Ask user if they want to proceed
proceed = input("Do you wish to proceed with documentation generation? (Y/N): ")
if proceed.upper() != "Y":
    print("Exiting")
    sys.exit()

# %%
# Ask user if they want to proceed
proceed = input("Do you wish to proceed with documentation generation? (Y/N): ")
if proceed.upper() != "Y":
    print("Exiting")
    sys.exit()

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",  # Change to your region
)

# Prepare input prompt
input_prompt = f"Given this repo. \n{repo_content}\ncomplete your instruction"

# Generate basic documentation
print("Generating basic documentation...")
request_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 4096,
    "system": BASIC_DOCS_SYSTEM_PROMPT,
    "messages": [
        {"role": "user", "content": input_prompt},
    ],
    "temperature": 0.5,
}

try:
    # You can replace this with any LLM API call (DeepSeek Code, CodeLlama, Llama 3.2)
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Replace with your desired model
        body=json.dumps(request_body)
    )
    
    # Parse response
    response_body = json.loads(response['body'].read().decode())
    basic_docs = response_body.get("content", [{"text": "No content received"}])[0]["text"]
    
    # Save basic documentation
    basic_docs_path = os.path.join(OUTPUT_DIR, f"{repo_name}-docs.md")
    with open(basic_docs_path, "w", encoding="utf-8") as file:
        file.write(SIGNATURE + basic_docs)
    print(f"Basic documentation saved to {basic_docs_path}")
    
    # Ask if user wants extended documentation
    proceed = input("Do you wish to generate extended documentation? (Y/N): ")
    if proceed.upper() == "Y":
        print("Generating extended documentation...")
        
        # Prepare extended documentation request
        extended_request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": BASIC_DOCS_SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": input_prompt},
                {"role": "assistant", "content": basic_docs},
                {"role": "user", "content": REFINED_DOCS_FOLLOW_UP_PROMPT},
            ],
            "temperature": 0.5,
        }
        
        # Call the LLM again for extended documentation
        extended_response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Replace with your desired model
            body=json.dumps(extended_request_body)
        )
        
        # Parse extended response
        extended_response_body = json.loads(extended_response['body'].read().decode())
        extended_docs = extended_response_body.get("content", [{"text": "No content received"}])[0]["text"]
        
        # Save extended documentation
        extended_docs_path = os.path.join(OUTPUT_DIR, f"{repo_name}-extended-docs.md")
        with open(extended_docs_path, "w", encoding="utf-8") as file:
            file.write(SIGNATURE + extended_docs)
        print(f"Extended documentation saved to {extended_docs_path}")
except Exception as e:
    print(f"Error generating documentation: {e}")

print("Documentation generation complete!")

# %%



