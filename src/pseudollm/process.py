import re
import json
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

def extract_tags(tagged_text):
    matches = re.findall(r"<to_pseudonym>(.*?)</to_pseudonym>", tagged_text)
    return matches


def generate_pseudonyms(entities):
    """
    Generate pseudonyms for a set of entities, considering their interdependencies.

    Args:
        entities (list of str): List of entities to pseudonymize.

    Returns:
        dict: Mapping of original entities to pseudonyms.
    """
    # Initialize OpenAI client
    client = OpenAI()

    # Construct a single prompt with all entities
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "system",
        "content":  [{
            "type": "text",
            "text": "You are a pseudonym generator. You will be provided with a list of personally identifiable information (PII). Your task is to assign suitable pseudonyms to each of the entities, using the pseudonym field. Ensure the pseudonyms match the tone and cultural context of the entities, contain the same number of words, and are consistent within the set."
    }]},
        {
            "role": "user", 
            "content": "\n".join(list(set(entities)))
        }
        ],
    temperature=1,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "math_reasoning",
            "schema": {
                "type": "object",
                "properties": {
                    'PII': {
                        'type': 'array', 
                        'items': {
                            'type': 'string'
                            }
                        },
                    'pseudonym': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                            }
                        }
                    },
                "required": ["PII", "pseudonym"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
    )

    # Parse the response into a dictionary
    response = completion.choices[0].message
    pseudonym_map = json.loads(response)
    
    return pseudonym_map
