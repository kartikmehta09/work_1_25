# Inputs
chunks = []  # List of repository content chunks
system_prompt = ""  # System prompt for Claude  
bedrock_client = None  # Initialized AWS Bedrock client
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"  # Model ID to use
max_tokens = 4096  # Maximum tokens for model response
temperature = 0.5  # Temperature for generation

# Initialize variables
all_responses = []
total_chunks = len(chunks)
i = 0

# Process each chunk with Claude
while i < total_chunks:
    chunk = chunks[i]
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
    
    # Move to next chunk
    i += 1

# Combine responses
combined_responses = ""
for j in range(len(all_responses)):
    if j > 0:
        combined_responses += "\n\n"
    combined_responses += all_responses[j]

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

# Call Claude for consolidation
consolidation_response = bedrock_client.invoke_model(
    modelId=model_id,
    body=json.dumps(consolidation_request)
)

# Parse response
consolidation_body = json.loads(consolidation_response['body'].read().decode())
final_docs = consolidation_body.get("content", [{"text": "No content received"}])[0]["text"]

# final_docs now contains the combined documentation

# Inputs
basic_docs = ""  # Basic documentation generated
follow_up_prompt = ""  # Follow-up prompt for extended documentation
bedrock_client = None  # Initialized AWS Bedrock client
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"  # Model ID to use
max_tokens = 4096  # Maximum tokens for model response
temperature = 0.5  # Temperature for generation

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

# Convert request to JSON string
request_json = json.dumps(request_body)

# Call Claude via Bedrock
response = bedrock_client.invoke_model(
    modelId=model_id,
    body=request_json
)

# Read response body
response_raw = response['body'].read()

# Decode response to string
response_string = response_raw.decode()

# Parse JSON
response_body = json.loads(response_string)

# Extract content from response
content_list = response_body.get("content", [{"text": "No content received"}])
extended_docs = content_list[0]["text"]

# extended_docs now contains the extended documentation