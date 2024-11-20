from openai import OpenAI

def annotate_pii(input_file, output_file, example_file):
    """
    Annotates a text file with tags for personally identifiable information (PII).

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output file to save the tagged text.
        example_file (str): Path to the example file with annotated tags.
    """
    # Initialize OpenAI client
    client = OpenAI()

    # Read input file
    with open(input_file, 'r') as f:
        file_content = f.read()

    # Read example file
    with open(example_file, 'r') as ex:
        example = ex.read()

    # Generate a completion using the model
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "Annotate all Personally Identifiable Information in the following text (e.g., names, places,  organizations, project names, etc.). "
                           "Use the tags <to_pseudonym> </to_pseudonym> to tag them. Do not use different tags. Just output the tagged text, without any further comment. "
                           "Do not change the original text."
            },
            {
                "role": "assistant",
                "content": example
            },
            {
                "role": "user",
                "content": f"Do the same on the following text. Just tag the text: do not change the original text.\n\nText:{file_content}"
            }
        ],
        temperature=1,
        max_tokens=5079,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Extract the model's response (the completion result)
    response = completion.choices[0].message.content

    # Write the output to a file
    with open(output_file, 'w') as out_f:
        out_f.write(response)

    print(f"Annotated file saved to {output_file}")
