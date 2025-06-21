#!/usr/bin/env python
# coding: utf-8

# In[14]:


import os
import sys
import ast
#import boto3
import json
import re
import datetime


# In[2]:


pwd


# In[41]:


timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
timestamp


# In[37]:


timestamp_1 = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
timestamp_1


# In[42]:


# Constants
REPO_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code'
OUTPUT_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code/output_path'

# Signature for generated documentation
SIGNATURE = """# Auto-generated Documentation

This documentation was automatically generated using a Large Language Model.

"""


# In[43]:


# Constants
REPO_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code'


# In[17]:


repo_name = os.path.basename(REPO_DIR)
repo_name


# In[18]:


OUTPUT_DIR


# In[44]:


output_file = os.path.join(OUTPUT_DIR, f"code_{timestamp}.txt")
output_file


# In[22]:


output_file = os.path.join(OUTPUT_DIR, f"code_{timestamp}.txt")
output_file


# # Constants
# REPO_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/doc_master_1'
# 
# 
# OUTPUT_DIR = '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/doc_master_1/output_path'
# 
# # Signature for generated documentation
# SIGNATURE = """# Auto-generated Documentation
# 
# This documentation was automatically generated using a Large Language Model.
# 
# """

# In[ ]:





# In[45]:


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


# In[46]:


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


# In[47]:


# Extract code from repository
print(f"Extracting code from {REPO_DIR}...")
#repo_name = os.path.basename(REPO_DIR)
#output_file = os.path.join(OUTPUT_DIR, f"{repo_name}_code2.txt")


# In[24]:


repo_name


# In[26]:


output_file

#"/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code/doc_1/code_2_doc_folder/output_path/code_2_doc_folder_code.txt"


# In[48]:


# Extract code from repository
# Master function 

#print(f"Extracting code from {REPO_DIR}...")
#repo_name = os.path.basename(REPO_DIR)
#output_file = os.path.join(OUTPUT_DIR, f"{repo_name}_code2.txt")

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


# In[49]:


# Estimate token size
with open(output_file, "r", encoding="utf-8") as file:
    repo_content = file.read()
    # Very simple estimation - approximately 4 characters per token
    token_size = len(repo_content) // 4
    print(f"Input token size estimate: {token_size}")


# # Estimate token size
# with open(output_file, "r", encoding="utf-8") as file:
#     repo_content = file.read()
#     # Very simple estimation - approximately 4 characters per token
#     token_size = len(repo_content) // 4
#     print(f"Input token size estimate: {token_size}")

# ## Path for output_file 
# ## output_path/source_code_code.txt
# 
# # Extracting code from /home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code...
# # '/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code/output_path/source_code_code.txt'

# Perform Chunking 

# In[29]:


CHUNK_SIZE = 1500
OVERLAP = 50
chunks = []
current_chunk = []
current_length = 0


# combined_content = repo_content

# for line in combined_content.split('\n'):
#     line_length = len(line) // 4
#     if current_length + line_length > CHUNK_SIZE:
#         chunks.append('\n'.join(current_chunk))
#         current_chunk = current_chunk[-OVERLAP//1000:]
#         current_length = sum(len(l)//4 for l in current_chunk)
#     current_chunk.append(line)
#     current_length += line_length

# In[31]:


for line in repo_content.split('\n'):
    line_length = len(line) // 4
    if current_length + line_length > CHUNK_SIZE:
        chunks.append('\n'.join(current_chunk))
        current_chunk = current_chunk[-OVERLAP//1000:]
        current_length = sum(len(l)//4 for l in current_chunk)
    current_chunk.append(line)
    current_length += line_length


# In[13]:


len(chunks)


# In[32]:


len(chunks)


# In[33]:


def chunk_repository_content(content, chunk_size=1500, overlap=50):
    """
    Divide repository content into overlapping chunks to fit within
    model context window.
    
    Args:
        content (str): The full repository content
        chunk_size (int): Target chunk size in tokens (estimated)
        overlap (int): Number of lines to overlap between chunks
        
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
    
    return chunks


# In[34]:


chunks_1 = chunk_repository_content(repo_content, chunk_size=1500, overlap=50)


# In[35]:


len(chunks_1)


# In[36]:


# after making chunks store output of chunks to a local file and then read chunks data from local file def chunk_repository_content(content, chunk_size=1500, overlap=50):


# In[52]:


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



# In[39]:


OUTPUT_DIR


# In[53]:


# Create chunks and save them to disk
chunks_1 = chunk_repository_content(
    content=repo_content,
    chunk_size=1500,
    overlap=50,
    output_dir=OUTPUT_DIR
    #,
    #repo_name=repo_name
)


# In[54]:


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


# In[56]:


chunks_2, metadata = load_chunks_from_file('/home/gpt/Documents/dev_env/fannie3/work_1_25/doc_1/source_code/output_path/chunks_20250422_062448.json')


# In[ ]:


import os
import json
import boto3
import datetime
from typing import List, Dict, Any, Tuple

def generate_documentation_from_chunks(
    chunks_file: str,
    output_dir: str,
    repo_name: str,
    bedrock_region: str = "us-east-1"
) -> Tuple[str, str]:
    """
    Generate technical documentation from repository chunks using Claude Sonnet.
    
    Args:
        chunks_file (str): Path to the JSON file containing repository chunks
        output_dir (str): Directory to save generated documentation
        repo_name (str): Name of the repository
        bedrock_region (str): AWS region for Bedrock
        
    Returns:
        Tuple[str, str]: Paths to basic and extended documentation files
    """
    # Load chunks from file
    chunks, metadata = load_chunks_from_file(chunks_file)
    
    # Initialize Bedrock client
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=bedrock_region
    )
    
    # Define system prompts
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

    # Documentation signature
    SIGNATURE = """# Auto-generated Documentation

This documentation was automatically generated using Claude Sonnet.

"""
    
    print(f"Generating basic documentation for {repo_name}...")
    
    # Process chunks for basic documentation
    basic_docs = process_chunks_with_claude(
        chunks=chunks,
        system_prompt=BASIC_DOCS_SYSTEM_PROMPT,
        bedrock_client=bedrock_runtime,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0"
    )
    
    # Save basic documentation
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    basic_docs_path = os.path.join(output_dir, f"{repo_name}-docs-{timestamp}.md")
    with open(basic_docs_path, "w", encoding="utf-8") as file:
        file.write(SIGNATURE + basic_docs)
    print(f"Basic documentation saved to {basic_docs_path}")
    
    # Ask if user wants extended documentation
    proceed = input("Do you wish to generate extended documentation? (Y/N): ")
    extended_docs_path = None
    
    if proceed.upper() == "Y":
        print("Generating extended documentation...")
        
        # Generate extended documentation using basic docs as context
        extended_docs = generate_extended_documentation(
            basic_docs=basic_docs,
            follow_up_prompt=REFINED_DOCS_FOLLOW_UP_PROMPT,
            bedrock_client=bedrock_runtime,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        # Save extended documentation
        extended_docs_path = os.path.join(output_dir, f"{repo_name}-extended-docs-{timestamp}.md")
        with open(extended_docs_path, "w", encoding="utf-8") as file:
            file.write(SIGNATURE + extended_docs)
        print(f"Extended documentation saved to {extended_docs_path}")
    
    return basic_docs_path, extended_docs_path

def load_chunks_from_file(chunks_file: str) -> Tuple[List[str], Dict[str, Any]]:
    """
    Load repository content chunks from a file.
    
    Args:
        chunks_file (str): Path to the JSON file containing chunks
        
    Returns:
        Tuple[List[str], Dict[str, Any]]: List of content chunks and metadata
    """
    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chunks = data.pop('chunks')
    metadata = data  # Contains timestamp, chunk_size, overlap, etc.
    
    print(f"Loaded {len(chunks)} chunks from {chunks_file}")
    print(f"Chunks metadata: {metadata}")
    
    return chunks, metadata

def process_chunks_with_claude(
    chunks: List[str],
    system_prompt: str,
    bedrock_client: Any,
    model_id: str,
    max_tokens: int = 4096,
    temperature: float = 0.5
) -> str:
    """
    Process repository chunks with Claude to generate documentation.
    
    Args:
        chunks (List[str]): List of repository content chunks
        system_prompt (str): System prompt for Claude
        bedrock_client: Initialized AWS Bedrock client
        model_id (str): Model ID to use
        max_tokens (int): Maximum tokens for model response
        temperature (float): Temperature for generation
        
    Returns:
        str: Combined documentation from all chunks
    """
    all_responses = []
    total_chunks = len(chunks)
    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{total_chunks}...")
        
        # Prepare request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": f"Given this code chunk: \n\n{chunk}\n\nGenerate documentation."}
            ],
            "temperature": temperature,
        }
        
        try:
            # Call Claude via Bedrock
            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read().decode())
            chunk_docs = response_body.get("content", [{"text": "No content received"}])[0]["text"]
            all_responses.append(chunk_docs)
            
            print(f"Successfully processed chunk {i+1}")
            
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")
            all_responses.append(f"Error processing chunk {i+1}: {str(e)}")
    
    # Combine responses and generate final documentation
    combined_responses = "\n\n".join(all_responses)
    
    # Create a consolidated documentation using Claude
    print("Generating consolidated documentation...")
    
    consolidation_prompt = f"""Below are documentation fragments generated from different parts of a code repository. 
Please consolidate these into a single, coherent documentation that eliminates redundancy and organizes the information logically:

{combined_responses}

Create a well-structured technical documentation that covers all the key aspects of the codebase.
"""
    
    consolidation_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": consolidation_prompt}
        ],
        "temperature": 0.3,  # Lower temperature for more consistent results
    }
    
    try:
        # Call Claude for consolidation
        consolidation_response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(consolidation_request)
        )
        
        # Parse response
        consolidation_body = json.loads(consolidation_response['body'].read().decode())
        final_docs = consolidation_body.get("content", [{"text": "No content received"}])[0]["text"]
        
        return final_docs
        
    except Exception as e:
        print(f"Error consolidating documentation: {e}")
        # Return the raw combined responses if consolidation fails
        return "# Documentation\n\n" + combined_responses

def generate_extended_documentation(
    basic_docs: str,
    follow_up_prompt: str,
    bedrock_client: Any,
    model_id: str,
    max_tokens: int = 4096,
    temperature: float = 0.5
) -> str:
    """
    Generate extended documentation based on basic documentation.
    
    Args:
        basic_docs (str): Basic documentation generated
        follow_up_prompt (str): Follow-up prompt for extended documentation
        bedrock_client: Initialized AWS Bedrock client
        model_id (str): Model ID to use
        max_tokens (int): Maximum tokens for model response
        temperature (float): Temperature for generation
        
    Returns:
        str: Extended documentation
    """
    # Prepare request body for Claude
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": "Here is the basic documentation of a code repository:"},
            {"role": "assistant", "content": basic_docs},
            {"role": "user", "content": follow_up_prompt}
        ],
        "temperature": temperature,
    }
    
    try:
        # Call Claude via Bedrock
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read().decode())
        extended_docs = response_body.get("content", [{"text": "No content received"}])[0]["text"]
        
        return extended_docs
        
    except Exception as e:
        print(f"Error generating extended documentation: {e}")
        return f"Error generating extended documentation: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Configuration
    REPO_DIR = '/path/to/repository'
    OUTPUT_DIR = '/path/to/output'
    
    # Find the latest chunks file in the output directory
    repo_name = os.path.basename(REPO_DIR)
    chunks_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"{repo_name}_chunks_") and f.endswith(".json")]
    
    if not chunks_files:
        print(f"No chunk files found for repository {repo_name}")
        exit(1)
        
    latest_chunks_file = sorted(chunks_files)[-1]  # Get the most recent file
    chunks_path = os.path.join(OUTPUT_DIR, latest_chunks_file)
    
    # Generate documentation
    basic_docs_path, extended_docs_path = generate_documentation_from_chunks(
        chunks_file=chunks_path,
        output_dir=OUTPUT_DIR,
        repo_name=repo_name
    )
    
    print("Documentation generation complete!")
    print(f"Basic documentation: {basic_docs_path}")
    if extended_docs_path:
        print(f"Extended documentation: {extended_docs_path}")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[55]:


ls


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[41]:


bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
responses = []

for i, chunk in enumerate(chunks):
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": chunk}]
        })
    )
    responses.append(json.loads(response["body"].read())["content"][0]["text"])


# In[40]:


chunks[0:2]


# In[21]:


len(repo_content) 


# In[30]:


len(repo_content) 


# In[22]:


token_size = len(repo_content) // 4
token_size


# In[ ]:





# In[19]:


test_1 = repo_content.split('\n')


# In[20]:


len(test_1)


# In[26]:


test_1[0:1]


# In[27]:


test_1[0:2]


# In[28]:


test_1[0:10]


# In[29]:


test_1[0:20]


# In[24]:


repo_content[0:1000]


# In[25]:


repo_content[0:10000]


# In[12]:


# Ask user if they want to proceed
proceed = input("Do you wish to proceed with documentation generation? (Y/N): ")
if proceed.upper() != "Y":
    print("Exiting")
    sys.exit()


# In[13]:


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


# In[ ]:




