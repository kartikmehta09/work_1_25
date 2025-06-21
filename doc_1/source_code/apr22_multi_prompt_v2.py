#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import sys
import ast
import json
import re
import datetime
import argparse
import nbformat
from typing import List, Dict, Any, Optional

# Signature for generated documentation
SIGNATURE = """# Auto-generated Documentation

This documentation was automatically generated using Claude Sonnet.

"""

# System prompts for the LLM
BASIC_DOCS_SYSTEM_PROMPT = """Your job is to act as the expert software engineer and provide detailed technical documentation broken into readable formats. 
You will be able to read the code file given as a converted single text with the Prefix "#File:" declaring the start of the file. 
Typescript projects are required to use pnpm for commands, python project if they have a pyproject.toml will be using poetry. MySQL databases are typically planetscale, and in that case we follow planetscales recommended use of prisma (if prisms ORM is used).
Documentation should be broken down into:
Introduction:
- Provide a brief overview of the file/project.
- Mention the purpose and core functionality of the code.
- Highlight the key features and potential use cases.
Codebase Overview:
- Provide an in-depth overview of the code architecture and design patterns used.
- Detail the functions, classes, and components, and their interactions.
Development Environment Setup:
- Step-by-step instructions for setting up the development environment, including necessary tools and dependencies.
- Include guidelines for configuring IDEs, linters, and other development tools.
Key Points of Complexity:
- Outline each keypoint of complexity
    - Breakdown each keypoint
Installation and Setup:
- Offer detailed instructions on installing and setting up the project.
- Include any prerequisites or dependencies required.
Getting Started:
- Guide users through a simple, initial setup or quick-start process.
- Include basic examples or a simple tutorial to help users begin using the code quickly.
The output should be detailed in standard markdown, using headers to improve readability.
"""

REFINED_DOCS_FOLLOW_UP_PROMPT = """You are instructed to further refine the documentation, there is no need to repeat basic content. Focus on delivering expert value insights for internal development handover outlined in the below criteria.
In-Depth Architecture Overview:
- Provide comprehensive descriptions of the code architecture, including data flow, component interactions, and external dependencies.
- Detail the critical architectural decisions and their justifications, discussing the trade-offs and alternatives considered.
Advanced Codebase Insights:
- Delve into complex functions and components, explaining intricate details that are crucial for understanding system behavior.
- Document any non-obvious implementation strategies and optimizations, explaining why they were necessary and how they impact the system.
Environment and Toolchain Deep Dive:
- Offer a detailed guide on the development, testing, and production environments, including specific configurations and environment parity practices.
- Describe the complete toolchain, including build systems, deployment pipelines, and any custom tooling.
Critical Dependency Analysis:
- Provide an exhaustive overview of external libraries, frameworks, and services the code depends on, including versioning, patching strategies, and known issues.
- Discuss how dependencies are managed, potential risks associated with them, and mitigation strategies.
Performance Considerations:
- Document performance benchmarks, profiling methods, and optimization strategies.
- Include potential performance bottlenecks and how to address them.
Security Protocols:
- Detail the security measures and protocols in place, including authentication, authorization, data encryption, and any security frameworks or libraries.
- Discuss security best practices, potential vulnerabilities, and their mitigations.
Testing and Quality Assurance:
- Elaborate on the testing strategy, including unit, integration, and end-to-end tests, highlighting any test-driven development (TDD) practices.
- Document approaches to quality assurance and test automation.
Troubleshooting and Debugging Guide:
- Provide a detailed guide for troubleshooting common issues, including debugging tips, logging best practices, and monitoring tools used.
Developer Onboarding:
- Create a focused onboarding guide for new developers, including key insights for understanding and working with this code.
- Include a glossary of terms, acronyms, and jargon used within the code to aid in understanding.
"""



# In[ ]:


# List of file extensions to include
CODE_EXTENSIONS = [
    ".py", ".ipynb", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h", 
    ".go", ".rs", ".php", ".rb", ".cs", ".sh", ".html", ".css", ".scss"
]

# List of directories and file patterns to exclude
EXCLUDED_DIRS = [
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
UTILITY_OR_CONFIG_FILES = ["hubconf.py", "setup.py", "package-lock.json"]
GITHUB_WORKFLOW_OR_DOCS = ["stale.py", "gen-card-", "write_model_card"]


# In[4]:


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate documentation for a code file.')
    parser.add_argument('input_file', help='Path to the file to document (.py, .ipynb, .js, etc.)')
    parser.add_argument('-o', '--output-dir', default=OUTPUT_DIR, help=f'Output directory (default: {OUTPUT_DIR})')
    parser.add_argument('-s', '--simulate', action='store_true', help='Run in simulation mode (no actual API calls)')
    parser.add_argument('-c', '--chunk-size', type=int, default=1500, help='Chunk size in tokens (default: 1500)')
    parser.add_argument('-ol', '--overlap', type=int, default=50, help='Overlap between chunks (default: 50)')
    return parser.parse_args()


# In[5]:


def is_valid_file(file_path: str) -> bool:
    """
    Check if a file should be processed based on extension and path filters.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file should be processed, False otherwise
    """
    # Skip if file path ends with "/"
    if file_path.endswith("/"):
        return False
    
    # Check if file has a desired extension
    if not any(file_path.endswith(ext) for ext in CODE_EXTENSIONS):
        return False
    
    # Check if file is in excluded directory
    check_path = file_path.replace("\\", "/")
    parts = check_path.split(os.sep)[1:]
    if any(part.startswith(".") for part in parts):
        return False
    
    if "test" in check_path.lower():
        return False
            
    # Check for excluded directories
    for excluded_dir in EXCLUDED_DIRS:
        if f"/{excluded_dir}/" in check_path or check_path.startswith(f"{excluded_dir}/"):
            return False
                
    # Check for utility or config files
    for file_name in UTILITY_OR_CONFIG_FILES:
        if file_name in check_path:
            return False
            
    # Check for GitHub workflow or docs files
    if not all(doc_file not in check_path for doc_file in GITHUB_WORKFLOW_OR_DOCS):
        return False
    
    return True


# In[ ]:


file_path = 'rag-using-llama-2-langchain-and-chromadb.ipynb'


test1 = is_valid_file(file_path)
test1


# In[ ]:


def extract_content(file_path: str, output_file: str) -> bool:
    """
    Extract content from Python scripts, Jupyter notebooks, or JavaScript files.
    Converts notebooks to Python scripts and filters out installation-related lines.
    
    Args:
        file_path (str): Path to the file
        output_file (str): Path to the output file
        
    Returns:
        bool: True if extraction was successful, False otherwise
    """
    # Check if the file is valid for processing
    if file_path.endswith("/"):
        print(f"File {file_path} ends with '/', skipping...")
        return False
    
    # Check file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    valid_extensions = [
        ".py", ".ipynb", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h", 
        ".go", ".rs", ".php", ".rb", ".cs", ".sh", ".html", ".css", ".scss"
    ]
    
    if file_extension not in valid_extensions:
        print(f"File {file_path} has unsupported extension, skipping...")
        return False
    
    # Check if file is in excluded directory
    check_path = file_path.replace("\\", "/")
    parts = check_path.split(os.sep)[1:]
    
    # Check for hidden directories
    if any(part.startswith(".") for part in parts):
        print(f"File {file_path} is in a hidden directory, skipping...")
        return False
    
    # Check for test files
    if "test" in check_path.lower():
        print(f"File {file_path} appears to be a test file, skipping...")
        return False
    
    # Check for excluded directories
    excluded_dirs = [
        "docs", "examples", "tests", "test", "__pycache__", 
        "scripts", "benchmarks", "node_modules", ".venv"
    ]
    
    for excluded_dir in excluded_dirs:
        if f"/{excluded_dir}/" in check_path or check_path.startswith(f"{excluded_dir}/"):
            print(f"File {file_path} is in excluded directory, skipping...")
            return False
    
    # Specific file exclusions
    utility_or_config_files = ["hubconf.py", "setup.py", "package-lock.json"]
    github_workflow_or_docs = ["stale.py", "gen-card-", "write_model_card"]
    
    if any(file_name in check_path for file_name in utility_or_config_files):
        print(f"File {file_path} is a utility/config file, skipping...")
        return False
    
    if any(doc_file in check_path for doc_file in github_workflow_or_docs):
        print(f"File {file_path} is a GitHub workflow/docs file, skipping...")
        return False
    
    try:
        # For Jupyter notebooks, convert to Python script first
        if file_extension == '.ipynb':
            try:
                import nbformat
                from nbconvert import PythonExporter
                
                print(f"Converting notebook {file_path} to Python script...")
                
                # Read the notebook
                with open(file_path, 'r', encoding='utf-8') as f:
                    notebook = nbformat.read(f, as_version=4)
                
                # Convert to Python
                python_exporter = PythonExporter()
                python_code, _ = python_exporter.from_notebook_node(notebook)
                
                # Process the converted Python code
                lines = python_code.split('\n')
                
                # Filter out installation-related lines
                filtered_lines = []
                for line in lines:
                    if not any(term in line for term in ["pip install", "Requirement already satisfied", "Installing", "Collecting", "Downloading"]):
                        filtered_lines.append(line)
                
                # Remove lines with less than 5 substantive lines
                if len(filtered_lines) < 5:
                    print(f"Converted notebook has less than 5 substantive lines, skipping...")
                    return False
                
                # Create output file with header
                with open(output_file, "w", encoding="utf-8") as outfile:
                    outfile.write(f"# File: {file_path} (converted from notebook)\n\n")
                    
                    # Try to clean comments and docstrings using AST
                    try:
                        source = "\n".join(filtered_lines)
                        tree = ast.parse(source)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and ast.get_docstring(node):
                                node.body = node.body[1:]  # Remove docstring
                            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                                node.value.s = ""  # Remove comments
                        cleaned_source = ast.unparse(tree)
                        outfile.write(cleaned_source)
                    except Exception as e:
                        print(f"AST parsing failed: {e}, using filtered lines")
                        outfile.write("\n".join(filtered_lines))
                
                print(f"Notebook converted and processed to {output_file}")
                return True
                
            except ImportError:
                print("nbformat or nbconvert not installed, processing notebook as text...")
                # If conversion libraries aren't available, revert to original processing
        
        # For Python scripts and other files
        with open(file_path, 'r', encoding='utf-8') as file_content:
            file_lines = file_content.readlines()
        
        # Filter out installation-related lines
        filtered_lines = []
        for line in file_lines:
            if not any(term in line for term in ["pip install", "Requirement already satisfied", "Installing", "Collecting", "Downloading"]):
                filtered_lines.append(line)
        
        # Skip files with insufficient substantive content
        substantive_lines = [
            line for line in filtered_lines
            if line.strip() and not line.strip().startswith("//")
        ]
        
        if len(substantive_lines) < 5:
            print(f"File {file_path} has less than 5 substantive lines after filtering, skipping...")
            return False
        
        # Create output file with header
        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write(f"# File: {file_path}\n\n")
            
            # Process based on file type
            if file_extension == '.py':
                # Python script processing
                try:
                    # Try to clean comments and docstrings using AST
                    source = "".join(filtered_lines)
                    tree = ast.parse(source)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and ast.get_docstring(node):
                            node.body = node.body[1:]  # Remove docstring
                        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                            node.value.s = ""  # Remove comments
                    cleaned_source = ast.unparse(tree)
                    outfile.write(cleaned_source)
                except Exception as e:
                    print(f"AST parsing failed: {e}, using filtered lines")
                    outfile.writelines(filtered_lines)
            
            elif file_extension in ['.js', '.jsx', '.ts', '.tsx']:
                # JavaScript file processing
                outfile.writelines(filtered_lines)
            
            else:
                # For other file types
                outfile.writelines(filtered_lines)
        
        print(f"File content extracted to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False


# In[ ]:


output_file = os.path.join(OUTPUT_DIR, f"code_{timestamp}.txt")
print(output_file)

file_path = 'rag-using-llama-2-langchain-and-chromadb.ipynb'
print(file_path)


test_2 = extract_content(file_path, output_file)

def estimate_token_size(content_file: str) -> int:
    """
    Estimate the token size of a file.
    
    Args:
        content_file (str): Path to the file
        
    Returns:
        int: Estimated token size
    """
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Very simple estimation - approximately 4 characters per token
        token_size = len(content) // 4
        print(f"Input token size estimate: {token_size}")
        return token_size
    except Exception as e:
        print(f"Error estimating token size: {e}")
        return 0


# In[ ]:


content_file = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code/output_path/code_20250422_181222.txt'

size_1 = estimate_token_size(content_file) 

size_1

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
timestamp

# Constants
REPO_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code'
OUTPUT_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code/output_path'

# Signature for generated documentation
SIGNATURE = """# Auto-generated Documentation

This documentation was automatically generated using a Large Language Model.

"""
repo_name = os.path.basename(REPO_DIR)
output_file = os.path.join(OUTPUT_DIR, f"code_{timestamp}.txt")
file_path = 'rag-using-llama-2-langchain-and-chromadb.ipynb'

file_path = 'rag-using-llama-2-langchain-and-chromadb.ipynb'


# In[17]:


output_dir = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code/output_path/'


# In[ ]:


#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import datetime
import argparse
import boto3
from typing import Optional

# Signature for generated documentation
SIGNATURE = """# Auto-generated Documentation

This documentation was automatically generated using Claude Sonnet.

"""

# System prompts for the LLM
BASIC_DOCS_SYSTEM_PROMPT = """Your job is to act as the expert software engineer and provide detailed technical documentation broken into readable formats. 
You will be able to read the code file given as a converted single text with the Prefix "#File:" declaring the start of the file. 
Typescript projects are required to use pnpm for commands, python project if they have a pyproject.toml will be using poetry. MySQL databases are typically planetscale, and in that case we follow planetscales recommended use of prisma (if prisms ORM is used).
Documentation should be broken down into:
Introduction:
- Provide a brief overview of the file/project.
- Mention the purpose and core functionality of the code.
- Highlight the key features and potential use cases.
Codebase Overview:
- Provide an in-depth overview of the code architecture and design patterns used.
- Detail the functions, classes, and components, and their interactions.
Development Environment Setup:
- Step-by-step instructions for setting up the development environment, including necessary tools and dependencies.
- Include guidelines for configuring IDEs, linters, and other development tools.
Key Points of Complexity:
- Outline each keypoint of complexity
    - Breakdown each keypoint
Installation and Setup:
- Offer detailed instructions on installing and setting up the project.
- Include any prerequisites or dependencies required.
Getting Started:
- Guide users through a simple, initial setup or quick-start process.
- Include basic examples or a simple tutorial to help users begin using the code quickly.
The output should be detailed in standard markdown, using headers to improve readability.
"""

REFINED_DOCS_FOLLOW_UP_PROMPT = """You are instructed to further refine the documentation, there is no need to repeat basic content. Focus on delivering expert value insights for internal development handover outlined in the below criteria.
In-Depth Architecture Overview:
- Provide comprehensive descriptions of the code architecture, including data flow, component interactions, and external dependencies.
- Detail the critical architectural decisions and their justifications, discussing the trade-offs and alternatives considered.
Advanced Codebase Insights:
- Delve into complex functions and components, explaining intricate details that are crucial for understanding system behavior.
- Document any non-obvious implementation strategies and optimizations, explaining why they were necessary and how they impact the system.
Environment and Toolchain Deep Dive:
- Offer a detailed guide on the development, testing, and production environments, including specific configurations and environment parity practices.
- Describe the complete toolchain, including build systems, deployment pipelines, and any custom tooling.
Critical Dependency Analysis:
- Provide an exhaustive overview of external libraries, frameworks, and services the code depends on, including versioning, patching strategies, and known issues.
- Discuss how dependencies are managed, potential risks associated with them, and mitigation strategies.
Performance Considerations:
- Document performance benchmarks, profiling methods, and optimization strategies.
- Include potential performance bottlenecks and how to address them.
Security Protocols:
- Detail the security measures and protocols in place, including authentication, authorization, data encryption, and any security frameworks or libraries.
- Discuss security best practices, potential vulnerabilities, and their mitigations.
Testing and Quality Assurance:
- Elaborate on the testing strategy, including unit, integration, and end-to-end tests, highlighting any test-driven development (TDD) practices.
- Document approaches to quality assurance and test automation.
Troubleshooting and Debugging Guide:
- Provide a detailed guide for troubleshooting common issues, including debugging tips, logging best practices, and monitoring tools used.
Developer Onboarding:
- Create a focused onboarding guide for new developers, including key insights for understanding and working with this code.
- Include a glossary of terms, acronyms, and jargon used within the code to aid in understanding.
"""

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate documentation for a code file.')
    parser.add_argument('input_file', help='Path to the file to document')
    parser.add_argument('-o', '--output-dir', default='output_docs', help='Output directory (default: output_docs)')
    parser.add_argument('-r', '--region', default='us-east-1', help='AWS region for Bedrock (default: us-east-1)')
    parser.add_argument('-m', '--model-id', default='anthropic.claude-3-sonnet-20240229-v1:0', 
                      help='Bedrock model ID (default: anthropic.claude-3-sonnet-20240229-v1:0)')
    return parser.parse_args()

def initialize_bedrock_client(region_name: str = 'us-east-1'):
    """
    Initialize and return an AWS Bedrock client.
    
    Args:
        region_name (str): AWS region name
    
    Returns:
        boto3.client: Initialized Bedrock client
    """
    try:
        # Initialize Bedrock client
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
        return bedrock_runtime
    except Exception as e:
        print(f"Error initializing Bedrock client: {e}")
        return None

def generate_basic_documentation(file_content: str, system_prompt: str, model_id: str, bedrock_client) -> str:
    """
    Generate basic documentation for the given file content using Claude Sonnet.
    
    Args:
        file_content (str): The content of the file to document
        system_prompt (str): System prompt for Claude
        model_id (str): Bedrock model ID
        bedrock_client: Initialized Bedrock client
        
    Returns:
        str: Generated documentation
    """
    if bedrock_client is None:
        print("Bedrock client is not available.")
        return "Error: Bedrock client is not available."
    
    print("Generating basic documentation...")
    
    # Prepare request body for Claude
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": f"Given this code file: \n\n{file_content}\n\nGenerate documentation."}
        ],
        "temperature": 0.5,
    }
    
    try:
        # Call Claude via Bedrock
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read().decode())
        documentation = response_body.get("content", [{"text": "No content received"}])[0]["text"]
        
        return documentation
        
    except Exception as e:
        print(f"Error generating documentation: {e}")
        return f"Error generating documentation: {str(e)}"

def generate_extended_documentation(basic_docs: str, follow_up_prompt: str, model_id: str, bedrock_client) -> str:
    """
    Generate extended documentation based on basic documentation.
    
    Args:
        basic_docs (str): Basic documentation
        follow_up_prompt (str): Follow-up prompt for extended documentation
        model_id (str): Bedrock model ID
        bedrock_client: Initialized Bedrock client
        
    Returns:
        str: Extended documentation
    """
    if bedrock_client is None:
        print("Bedrock client is not available.")
        return "Error: Bedrock client is not available."
    
    print("Generating extended documentation...")
    
    try:
        # Call Claude for extended documentation
        extended_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {"role": "user", "content": "Here is the basic documentation for a code file:"},
                {"role": "assistant", "content": basic_docs},
                {"role": "user", "content": follow_up_prompt}
            ],
            "temperature": 0.5,
        }
        
        extended_response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(extended_request)
        )
        
        # Parse response
        extended_body = json.loads(extended_response['body'].read().decode())
        extended_docs = extended_body.get("content", [{"text": "No content received"}])[0]["text"]
        
        return extended_docs
        
    except Exception as e:
        print(f"Error generating extended documentation: {e}")
        return f"Error generating extended documentation: {str(e)}"

def main():
    """Main function to run the script."""
    # Parse command line arguments
    args = parse_arguments()
    
    input_file = args.input_file
    output_dir = args.output_dir
    region_name = args.region
    model_id = args.model_id
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if input file exists
    if not os.path.isfile(input_file):
        print(f"Input file '{input_file}' does not exist.")
        return
    
    # Determine file type and base name
    file_name = os.path.basename(input_file)
    file_base_name = os.path.splitext(file_name)[0]
    
    # Generate timestamp for output files
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            file_content = file.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    # Add file header
    file_content_with_header = f"# File: {input_file}\n\n{file_content}"
    
    # Initialize Bedrock client
    bedrock_client = initialize_bedrock_client(region_name)
    if bedrock_client is None:
        print("Failed to initialize Bedrock client. Exiting.")
        return
    
    # Generate basic documentation
    basic_docs = generate_basic_documentation(
        file_content=file_content_with_header,
        system_prompt=BASIC_DOCS_SYSTEM_PROMPT,
        model_id=model_id,
        bedrock_client=bedrock_client
    )
    
    # Save basic documentation
    basic_docs_path = os.path.join(output_dir, f"{file_base_name}-docs-{timestamp}.md")
    with open(basic_docs_path, "w", encoding="utf-8") as file:
        file.write(SIGNATURE + basic_docs)
    print(f"Basic documentation saved to {basic_docs_path}")
    
    # Ask if user wants extended documentation
    proceed = input("Do you wish to generate extended documentation? (Y/N): ")
    if proceed.upper() == "Y":
        # Generate extended documentation
        extended_docs = generate_extended_documentation(
            basic_docs=basic_docs,
            follow_up_prompt=REFINED_DOCS_FOLLOW_UP_PROMPT,
            model_id=model_id,
            bedrock_client=bedrock_client
        )
        
        # Save extended documentation
        extended_docs_path = os.path.join(output_dir, f"{file_base_name}-extended-docs-{timestamp}.md")
        with open(extended_docs_path, "w", encoding="utf-8") as file:
            file.write(SIGNATURE + extended_docs)
        
        print(f"Extended documentation saved to {extended_docs_path}")
    
    print("Documentation generation complete!")

if __name__ == "__main__":
    main()

