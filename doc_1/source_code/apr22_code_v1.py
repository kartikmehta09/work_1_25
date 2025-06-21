#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
import ast
#import boto3
import json
import re
import datetime


# In[2]:


pwd


# In[3]:


timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
print(timestamp)

# Constants
REPO_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code'
print(REPO_DIR)

OUTPUT_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code/output_path'
print(OUTPUT_DIR)

# Signature for generated documentation
SIGNATURE = """# Auto-generated Documentation

This documentation was automatically generated using a Large Language Model.

"""


# In[4]:


output_file = os.path.join(OUTPUT_DIR, f"code_{timestamp}.txt")
output_file


# In[5]:


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


# In[6]:


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


# In[7]:


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


# In[8]:


# Estimate token size
with open(output_file, "r", encoding="utf-8") as file:
    repo_content = file.read()
    # Very simple estimation - approximately 4 characters per token
    token_size = len(repo_content) // 4
    print(f"Input token size estimate: {token_size}")


# In[11]:


def chunk_repository_content(content, chunk_size=1500, overlap=50, output_dir=None, repo_name=None):
    """
    Divide repository content into overlapping chunks and optionally save to disk.
    
    Args:
        content (str): The full repository content
        chunk_size (int): Target chunk size in tokens (estimated)
        overlap (int): Number of lines to overlap between chunks
        output_dir (str): Directory to save chunks (if None, won't save)
        repo_name (str): Repository name for filename
        
    Returns:
        list: List of content chunks
    """
    chunks = []
    lines = content.split('\n')
    current_chunk = []
    current_length = 0
    
    # Simple token estimation - approximately 4 chars per token
    for line in lines:
        line_length = len(line) // 4
        
        # If adding this line would exceed chunk size, save current chunk
        if current_length + line_length > chunk_size:
            chunks.append('\n'.join(current_chunk))
            # Keep overlap lines for the next chunk
            current_chunk = current_chunk[-overlap:]
            current_length = sum(len(l) // 4 for l in current_chunk)
        
        # Add line to current chunk
        current_chunk.append(line)
        current_length += line_length
    
    # Add the final chunk if not empty
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    # Save chunks to file if output directory is provided
    # if output_dir and repo_name:
    if output_dir:    
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        chunks_file = os.path.join(output_dir, f"chunks_{timestamp}.json")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save chunks to JSON file
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'chunk_size': chunk_size,
                'overlap': overlap,
                'total_chunks': len(chunks),
                'chunks': chunks
            }, f, indent=2)
        
        print(f"Saved {len(chunks)} chunks to {chunks_file}")
    
    return chunks


# In[12]:


chunks = chunk_repository_content(repo_content, chunk_size=1500, overlap=50)


# In[13]:


# Create chunks and save them to disk
chunks_1 = chunk_repository_content(
    content=repo_content,
    chunk_size=1500,
    overlap=50,
    output_dir=OUTPUT_DIR
    #,
    #repo_name=repo_name
)


# In[14]:


def load_chunks_from_file(chunks_file):
    """
    Load repository content chunks from a file.
    
    Args:
        chunks_file (str): Path to the JSON file containing chunks
        
    Returns:
        list: List of content chunks
        dict: Metadata about the chunks
    """
    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chunks = data.pop('chunks')
    metadata = data  # Contains timestamp, chunk_size, overlap, etc.
    
    print(f"Loaded {len(chunks)} chunks from {chunks_file}")
    print(f"Chunks metadata: {metadata}")
    
    return chunks, metadata


# In[ ]:


output_path/chunks_20250422_064723.json


# In[15]:


chunks_1, metadata_1 = load_chunks_from_file('/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code/output_path/chunks_20250422_064723.json')


# In[17]:


# Initialize Bedrock client
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name=bedrock_region)


# In[18]:


# Process chunks for basic documentation
basic_docs = process_chunks_with_claude(
        chunks=chunks,
        system_prompt=BASIC_DOCS_SYSTEM_PROMPT,
        bedrock_client=bedrock_runtime,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0"
    )


# In[19]:


# Generate extended documentation using basic docs as context
extended_docs = generate_extended_documentation(
            basic_docs=basic_docs,
            follow_up_prompt=REFINED_DOCS_FOLLOW_UP_PROMPT,
            bedrock_client=bedrock_runtime,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0"
        )


# In[ ]:




