def apply_template_with_claude(chunk, template_rules, bedrock_client, model_id):
    """Use Anthropic Claude on Amazon Bedrock to reformat the chunk."""
    # Prepare the content for the LLM
    chunk_text = ""

    if chunk["header"]:
        chunk_text += f"# Header: {chunk['header']['text']}\n\n"

    if chunk["subheader"]:
        chunk_text += f"## Subheader: {chunk['subheader']['text']}\n\n"

    for item in chunk["content"]:
        if item["type"] == "paragraph":
            chunk_text += f"{item['text']}\n\n"

    # Create a prompt for Claude
    prompt = f"""
    I have a document section that needs to be reformatted according to a new template.

    The new template has these formatting rules:
    - Headers: {template_rules['header']}
    - Subheaders: {template_rules['subheader']}
    - Paragraphs: {template_rules['paragraph']}

    Here's the content to reformat:

    {chunk_text}

    Please reformat this content according to the template rules, 
    preserving all original information.
    Return the reformatted content with clear separation between headers, 
    subheaders, and paragraphs.

    Format your response like this:
    # HEADER: <header text>
    ## SUBHEADER: <subheader text>
    PARAGRAPH: <paragraph text>

    (Only include header/subheader if present in the original)
    """

    # Create the request body for Claude
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "temperature": 0.2,
        "system": "You are a document formatting assistant.",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        # Call the Bedrock API
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )

        # Parse the response
        response_body = json.loads(response["body"].read())
        reformatted_text = response_body["content"][0]["text"]

        # Parse the reformatted content back into structured form
        reformatted_structure = parse_llm_response(reformatted_text, template_rules)

        return reformatted_structure

    except Exception as e:
        print(f"Error processing chunk with Claude: {e}")
        # Return the original chunk structure as fallback
        if chunk["subheader"]:
            return [chunk["header"]] + [chunk["subheader"]] + chunk["content"]
        else:
            return [chunk["header"]] + chunk["content"]