import os
import sys
import ast
import boto3
import json
import argparse

# Signature for generated documentation
SIGNATURE = """# Auto-generated Documentation

This documentation was automatically generated using a Large Language Model.

"""

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

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Generate technical documentation for code repositories")
parser.add_argument("--repo", default="doc_1/code_2_doc_folder", help="Path to the code repository")
parser.add_argument("--output", default="doc_1/code_2_doc_folder/output_path", help="Path to the output directory")
parser.add_argument("--model", default="anthropic.claude-3-sonnet-20240229-v1:0", help="Model ID to use")
parser.add_argument("--region", default="us-east-1", help="AWS region for Bedrock")
parser.add_argument("--extended", action="store_true", help="Generate extended documentation")
parser.add_argument("--force", action="store_true", help="Skip token size confirmation")
args = parser.parse_args()

# Set repository and output directories
REPO_DIR = args.repo
OUTPUT_DIR = args.output

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

# Print startup message
print(f"Documentation Generator")
print(f"=====================")
print(f"Repository: {REPO_DIR}")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"Model: {args.model}")
print()

# Validate repository path
if not os.path.exists(REPO_DIR):
    print(f"Error: Repository path '{REPO_DIR}' does not exist.")
    sys.exit(1)

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
                    relative_path = os.path.relpath(file_path, REPO_DIR)
                    outfile.write(f"# File: {relative_path}\n")
                    
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
                    # Handle Jupyter notebooks
                    elif file_path.endswith(".ipynb"):
                        try:
                            import json
                            notebook = json.load(open(file_path, 'r', encoding='utf-8'))
                            for cell in notebook.get('cells', []):
                                if cell.get('cell_type') == 'code':
                                    outfile.write("```python\n")
                                    outfile.write(''.join(cell.get('source', [])))
                                    outfile.write("\n```\n\n")
                        except:
                            outfile.write("# Failed to parse notebook\n")
                            outfile.writelines(file_lines)
                    else:
                        # For non-Python files, write original content
                        outfile.writelines(file_lines)
                        
                    outfile.write("\n\n")
                    print(f"  Processed: {relative_path}")
            except Exception as e:
                print(f"  Error reading file {file_path}: {e}")

print(f"Code extracted to {output_file}")

# Estimate token size
with open(output_file, "r", encoding="utf-8") as file:
    repo_content = file.read()
    # Very simple estimation - approximately 4 characters per token
    token_size = len(repo_content) // 4
    print(f"Input token size estimate: {token_size}")
    print(f"File size: {os.path.getsize(output_file) / 1024:.2f} KB")

# Ask user if they want to proceed
if not args.force:
    proceed = input("Do you wish to proceed with documentation generation? (Y/N): ")
    if proceed.upper() != "Y":
        print("Exiting")
        sys.exit()

try:
    # Initialize Bedrock client
    print(f"Initializing AWS Bedrock client in region {args.region}...")
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=args.region,
    )

    # Prepare input prompt
    input_prompt = f"Given this repo. \n{repo_content}\ncomplete your instruction"

    # Generate basic documentation
    print("Generating basic documentation...")
    
    # Determine max tokens based on model
    max_tokens = 4096
    if "claude-3" in args.model:
        if "opus" in args.model:
            max_tokens = 4096
        elif "sonnet" in args.model:
            max_tokens = 4096
        elif "haiku" in args.model:
            max_tokens = 2048
    
    # Set up request for different model types
    if "anthropic" in args.model or "claude" in args.model:
        # Claude-specific request format
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": BASIC_DOCS_SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": input_prompt},
            ],
            "temperature": 0.5,
        }
    else:
        # Generic format for other models (CodeLLama, DeepSeek, etc.)
        request_body = {
            "prompt": BASIC_DOCS_SYSTEM_PROMPT + "\n\n" + input_prompt,
            "max_tokens": max_tokens,
            "temperature": 0.5,
        }
    
    # Invoke model
    response = bedrock_runtime.invoke_model(
        modelId=args.model,
        body=json.dumps(request_body)
    )
    
    # Parse response based on model
    response_body = json.loads(response['body'].read().decode())
    
    # Extract content based on model type
    if "anthropic" in args.model or "claude" in args.model:
        basic_docs = response_body.get("content", [{"text": "No content received"}])[0]["text"]
    else:
        # Format for other models like CodeLLama, DeepSeek, etc.
        basic_docs = response_body.get("generation", response_body.get("text", response_body.get("completion", "No content received")))
    
    # Save basic documentation
    basic_docs_path = os.path.join(OUTPUT_DIR, f"{repo_name}-docs.md")
    with open(basic_docs_path, "w", encoding="utf-8") as file:
        file.write(SIGNATURE + basic_docs)
    print(f"Basic documentation saved to {basic_docs_path}")
    
    # Generate extended documentation if requested
    if args.extended or (not args.force and input("Do you wish to generate extended documentation? (Y/N): ").upper() == "Y"):
        print("Generating extended documentation...")
        
        # Prepare extended documentation request
        if "anthropic" in args.model or "claude" in args.model:
            # Claude-specific format
            extended_request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": BASIC_DOCS_SYSTEM_PROMPT,
                "messages": [
                    {"role": "user", "content": input_prompt},
                    {"role": "assistant", "content": basic_docs},
                    {"role": "user", "content": REFINED_DOCS_FOLLOW_UP_PROMPT},
                ],
                "temperature": 0.5,
            }
        else:
            # Generic format
            extended_request_body = {
                "prompt": BASIC_DOCS_SYSTEM_PROMPT + "\n\n" + input_prompt + "\n\n" + basic_docs + "\n\n" + REFINED_DOCS_FOLLOW_UP_PROMPT,
                "max_tokens": max_tokens,
                "temperature": 0.5,
            }
        
        # Call the model for extended documentation
        extended_response = bedrock_runtime.invoke_model(
            modelId=args.model,
            body=json.dumps(extended_request_body)
        )
        
        # Parse extended response
        extended_response_body = json.loads(extended_response['body'].read().decode())
        
        # Extract content based on model type
        if "anthropic" in args.model or "claude" in args.model:
            extended_docs = extended_response_body.get("content", [{"text": "No content received"}])[0]["text"]
        else:
            # Format for other models
            extended_docs = extended_response_body.get("generation", extended_response_body.get("text", extended_response_body.get("completion", "No content received")))
        
        # Save extended documentation
        extended_docs_path = os.path.join(OUTPUT_DIR, f"{repo_name}-extended-docs.md")
        with open(extended_docs_path, "w", encoding="utf-8") as file:
            file.write(SIGNATURE + extended_docs)
        print(f"Extended documentation saved to {extended_docs_path}")

    print("Documentation generation complete!")
    
except Exception as e:
    print(f"Error generating documentation: {e}")
    import traceback
    traceback.print_exc()

# If running as script, execute the code
if __name__ == "__main__":
    pass  # Main code already executed
