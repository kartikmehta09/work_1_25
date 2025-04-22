#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
import ast
import json
import re
import datetime
import argparse
import nbformat
from typing import List, Dict, Any, Optional


# In[2]:


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


# In[3]:


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


# In[6]:


def extract_content(file_path: str, output_file: str) -> bool:
    """
    Extract content from Python scripts, Jupyter notebooks, or JavaScript files.
    
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
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file_content:
            file_lines = file_content.readlines()
        
        # Skip files with insufficient substantive content
        lines = [
            line
            for line in file_lines
            if line.strip() and not line.strip().startswith("//")
        ]
        
        if len(lines) < 5:  # Skip files with less than 5 substantive lines
            print(f"File {file_path} has less than 5 substantive lines, skipping...")
            return False
        
        # Create output file with header
        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write(f"# File: {file_path}\n\n")
            
            # Process based on file type
            if file_extension == '.py':
                # Python script processing
                try:
                    # Try to clean comments and docstrings using AST
                    source = "".join(file_lines)
                    tree = ast.parse(source)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and ast.get_docstring(node):
                            node.body = node.body[1:]  # Remove docstring
                        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                            node.value.s = ""  # Remove comments
                    cleaned_source = ast.unparse(tree)
                    outfile.write(cleaned_source)
                except Exception as e:
                    print(f"AST parsing failed: {e}, using original source")
                    # If ast parsing fails, write the original source
                    outfile.writelines(file_lines)
            
            elif file_extension == '.ipynb':
                # Jupyter notebook processing
                try:
                    import nbformat
                    with open(file_path, 'r', encoding='utf-8') as f:
                        notebook = nbformat.read(f, as_version=4)
                    
                    # Process cells
                    for cell_idx, cell in enumerate(notebook.cells):
                        cell_type = cell.cell_type
                        source = cell.source
                        
                        # Add cell metadata
                        outfile.write(f"## Cell {cell_idx+1} ({cell_type})\n\n")
                        
                        if cell_type == 'code':
                            outfile.write("```python\n")
                            outfile.write(source)
                            outfile.write("\n```\n\n")
                            
                            # If there's output, include it
                            if hasattr(cell, 'outputs') and cell.outputs:
                                outfile.write("### Output:\n\n")
                                for output in cell.outputs:
                                    if output.output_type == 'stream':
                                        outfile.write("```\n")
                                        outfile.write(output.text)
                                        outfile.write("\n```\n\n")
                                    elif output.output_type == 'execute_result' and 'text/plain' in output.data:
                                        outfile.write("```\n")
                                        outfile.write(output.data['text/plain'])
                                        outfile.write("\n```\n\n")
                        
                        elif cell_type == 'markdown':
                            outfile.write(source)
                            outfile.write("\n\n")
                
                except ImportError:
                    print("nbformat not installed, writing raw content")
                    outfile.write("```\n")
                    outfile.writelines(file_lines)
                    outfile.write("\n```\n")
                except Exception as e:
                    print(f"Error processing notebook: {e}, writing raw content")
                    outfile.write("```\n")
                    outfile.writelines(file_lines)
                    outfile.write("\n```\n")
            
            elif file_extension in ['.js', '.jsx', '.ts', '.tsx']:
                # JavaScript file processing
                # Simply write the original content
                outfile.writelines(file_lines)
            
            else:
                # For other file types, just write the content
                outfile.writelines(file_lines)
        
        print(f"File content extracted to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False


# In[7]:


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


# In[8]:


def chunk_content(content_file: str, chunk_size: int = 1500, overlap: int = 50, output_dir: Optional[str] = None) -> List[str]:
    """
    Divide file content into overlapping chunks and optionally save to disk.
    
    Args:
        content_file (str): Path to the file containing content
        chunk_size (int): Target chunk size in tokens (estimated)
        overlap (int): Number of lines to overlap between chunks
        output_dir (str): Directory to save chunks (if None, won't save)
        
    Returns:
        list: List of content chunks
    """
    # Read content from file
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
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


# In[9]:


def load_chunks_from_file(chunks_file: str) -> tuple:
    """
    Load repository content chunks from a file.
    
    Args:
        chunks_file (str): Path to the JSON file containing chunks
        
    Returns:
        tuple: List of content chunks and metadata dict
    """
    try:
        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data.pop('chunks')
        metadata = data  # Contains timestamp, chunk_size, overlap, etc.
        
        print(f"Loaded {len(chunks)} chunks from {chunks_file}")
        print(f"Chunks metadata: {metadata}")
        
        return chunks, metadata
    except Exception as e:
        print(f"Error loading chunks from file: {e}")
        return [], {}


# In[10]:


def process_chunks_with_claude(chunks: List[str], system_prompt: str, simulation: bool = True) -> str:
    """
    Process content chunks with Claude to generate documentation.
    
    Args:
        chunks (list): List of content chunks
        system_prompt (str): System prompt for Claude
        simulation (bool): Whether to run in simulation mode
        
    Returns:
        str: Combined documentation from all chunks
    """
    all_responses = []
    total_chunks = len(chunks)
    
    # If in simulation mode, return a placeholder
    if simulation:
        print("Running in simulation mode. No actual API calls will be made.")
        for i in range(min(3, total_chunks)):  # Process only a few chunks in simulation
            print(f"Simulating processing chunk {i+1}/{total_chunks}...")
            all_responses.append(f"# Documentation for Chunk {i+1}\n\nThis is simulated documentation for chunk {i+1}.")
        
        return "\n\n".join(all_responses)
    
    # Real processing with Claude via AWS Bedrock
    try:
        import boto3
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",  # Change to your region
        )
    except ImportError:
        print("boto3 library not installed. Please install it with 'pip install boto3'.")
        print("Falling back to simulation mode.")
        return process_chunks_with_claude(chunks, system_prompt, simulation=True)
    except Exception as e:
        print(f"Error initializing Bedrock client: {e}")
        print("Falling back to simulation mode.")
        return process_chunks_with_claude(chunks, system_prompt, simulation=True)
    
    # Process chunks with Claude
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{total_chunks}...")
        
        # Prepare request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": f"Given this code chunk: \n\n{chunk}\n\nGenerate documentation."}
            ],
            "temperature": 0.5,
        }
        
        try:
            # Call Claude via Bedrock
            response = bedrock_runtime.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Update with current model version
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
    
    # Combine responses
    combined_responses = "\n\n".join(all_responses)
    
    # Create a consolidated documentation using Claude
    print("Generating consolidated documentation...")
    
    consolidation_prompt = f"""Below are documentation fragments generated from different parts of a code file. 
Please consolidate these into a single, coherent documentation that eliminates redundancy and organizes the information logically:

{combined_responses}

Create a well-structured technical documentation that covers all the key aspects of the code.
"""
    
    try:
        # Call Claude for consolidation
        consolidation_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": consolidation_prompt}
            ],
            "temperature": 0.3,  # Lower temperature for more consistent results
        }
        
        consolidation_response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
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


# In[11]:


def generate_extended_documentation(basic_docs: str, follow_up_prompt: str, simulation: bool = True) -> str:
    """
    Generate extended documentation based on basic documentation.
    
    Args:
        basic_docs (str): Basic documentation
        follow_up_prompt (str): Follow-up prompt for extended documentation
        simulation (bool): Whether to run in simulation mode
        
    Returns:
        str: Extended documentation
    """
    if simulation:
        print("Simulating extended documentation generation...")
        return "# Extended Documentation (Simulation)\n\nThis is simulated extended documentation based on the basic documentation."
    
    # Real processing with Claude via AWS Bedrock
    try:
        import boto3
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",  # Change to your region
        )
    except ImportError:
        print("boto3 library not installed. Please install it with 'pip install boto3'.")
        print("Falling back to simulation mode.")
        return generate_extended_documentation(basic_docs, follow_up_prompt, simulation=True)
    except Exception as e:
        print(f"Error initializing Bedrock client: {e}")
        print("Falling back to simulation mode.")
        return generate_extended_documentation(basic_docs, follow_up_prompt, simulation=True)
    
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
        
        extended_response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(extended_request)
        )
        
        # Parse response
        extended_body = json.loads(extended_response['body'].read().decode())
        extended_docs = extended_body.get("content", [{"text": "No content received"}])[0]["text"]
        
        return extended_docs
        
    except Exception as e:
        print(f"Error generating extended documentation: {e}")
        return f"Error generating extended documentation: {str(e)}"


# In[ ]:




