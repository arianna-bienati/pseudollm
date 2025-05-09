import json
import logging
import re

from difflib import unified_diff

from openai import OpenAI
import tiktoken

def setup_logger(log_file):
    """Set up a simple file logger"""
    logger = logging.getLogger('pseudonymization')
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(message)s') 
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def num_tokens_from_messages(messages, model):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")
    if model in {
        "gpt-3.5-turbo-0125",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06"
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0125.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0125")
    elif "gpt-4o-mini" in model:
        print("Warning: gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-mini-2024-07-18.")
        return num_tokens_from_messages(messages, model="gpt-4o-mini-2024-07-18")
    elif "gpt-4o" in model:
        print("Warning: gpt-4o and gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-2024-08-06.")
        return num_tokens_from_messages(messages, model="gpt-4o-2024-08-06")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def annotate_pii(input_file, output_file, example_file, gpt_model = "gpt-4o-mini"):
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

    prompt = [
            {
                "role": "user",
                "content": "Annotate all Personally Identifiable Information in the following text (e.g., names, places, organizations, project names, etc.). Use the tags <to_pseudonym type = 'value'> </to_pseudonym> to tag them. Use the 'type' attribute to detail which kind of PII it is. You can choose between four types: PER for persons, LOC for locations, ORG for organizations and MISC for anything else. Just output the tagged text, without any further comment. Do not change the original text."
            },
            {
                "role": "assistant",
                "content": example
            },
            {
                "role": "user",
                "content": f"Do the same on the following text. Just tag the text: do not change the original text.\n\nText:{file_content}"
            }
        ]
    
    prompt_tokens = num_tokens_from_messages(prompt, gpt_model)

    # Generate a completion using the model
    completion = client.chat.completions.create(
        model=gpt_model,
        messages=prompt,
        temperature=0,
        max_tokens=prompt_tokens + 200
    )

    # Extract the model's response (the completion result)
    response = completion.choices[0].message.content

    # Write the output to a file
    with open(output_file, 'w') as out_f:
        out_f.write(response)

def extract_tags(tagged_text):
    matches = re.findall(r'<to_pseudonym type = "[^"]+">(.*?)</to_pseudonym>', tagged_text)
    unique_matches = list(set(matches))
    return unique_matches

def generate_pseudonyms(entities, gpt_model = "gpt-4o"):
    """
    Generate pseudonyms for a set of entities, considering their interdependencies.

    Args:
        entities (list of str): List of entities to pseudonymize.

    Returns:
        dict: Mapping of original entities to pseudonyms.
    """
    # Initialize OpenAI client
    client = OpenAI()

    prompt = [
        {
        "role": "system",
        "content":  "You are a pseudonym generator. You will be provided with a list of personally identifiable information (PII). Your task is to assign suitable pseudonyms to each of the entities, using the pseudonym field. Ensure the pseudonyms match the tone and cultural context of the entities, contain the same number of words, and are consistent within the set."
        },
        {
            "role": "user", 
            "content": "\n".join(entities)
        }
        ]

    prompt_tokens = num_tokens_from_messages(prompt, gpt_model)

    # Construct a single prompt with all entities
    completion = client.chat.completions.create(
    model=gpt_model,
    messages=prompt,
    temperature=1,
    max_tokens=prompt_tokens*2,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "map_pseudonyms",
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
    response = completion.choices[0].message.content
    pseudonym_map = json.loads(response)
    
    return pseudonym_map

def pseudonymization(tagged_text, pseudonym_map, logger):
    """
    Replace entities tagged as <to_pseudonym> in the text with pseudonyms.
    
    Args:
        tagged_text (str): Text with entities tagged as <to_pseudonym>{entity}</to_pseudonym>
        pseudonym_map (dict): Dictionary with 'PII' and 'pseudonym' lists
        logger (logging.Logger): Logger for tracking replacements
    """    
    # Extract PII and pseudonym arrays
    pii_list = pseudonym_map.get("PII", [])
    pseudonym_list = pseudonym_map.get("pseudonym", [])
    
    # Input validation
    if not pii_list or not pseudonym_list:
        logger.error("Empty PII or pseudonym list")
        raise ValueError("Both PII and pseudonym lists must be non-empty")
    
    if len(pii_list) != len(pseudonym_list):
        logger.error(f"List length mismatch: {len(pii_list)} PIIs vs {len(pseudonym_list)} pseudonyms")
        raise ValueError("PII and pseudonym lists must have the same length")
    
    # Perform replacements with logging
    replacements_made = 0
    for original, pseudonym in zip(pii_list, pseudonym_list):
        tagged_entity_pattern = rf'<to_pseudonym type = "[^"]+">{re.escape(original)}</to_pseudonym>'
        tagged_text = re.sub(tagged_entity_pattern, pseudonym, tagged_text)
        replacements_made += 1
        logger.info(f"Replaced '{original}' with '{pseudonym}'")
    
    return tagged_text, replacements_made

def ner_pseudonymization(tagged_text):
    """
    Replace entities in <to_pseudonym type="value">{entity}</to_pseudonym> tags 
    with their 'type' attribute value wrapped in square brackets.

    Args:
        tagged_text (str): The text containing <to_pseudonym type="value">{entity}</to_pseudonym> tags.

    Returns:
        str: Text with entities replaced by their 'type' attribute values wrapped in square brackets.
    """
    # Replace each <to_pseudonym type="value">{entity}</to_pseudonym> with [type]
    return re.sub(
        r'<to_pseudonym type = "([^"]+)">.*?</to_pseudonym>', 
        lambda match: f"[{match.group(1)}]", 
        tagged_text
    )

def validate_pseudonymization(file1, file2):
    """
    Validates two file versions by comparing their contents using difflib.
    Counts insertions and deletions and ensures they are equal.
    If not, prints the filename stem of the first file.

    Args:
        file1_path (str): Path to the first file.
        file2_path (str): Path to the second file.
    """

    # Read file contents
    file1_content = file1.read_text()
    file2_content = file2.read_text()

    # Tokenize file contents by splitting on whitespace
    file1_tokens = file1_content.split()
    file2_tokens = file2_content.split()

    # Use difflib to get a unified diff
    diff = unified_diff(file1_tokens, file2_tokens, lineterm='')

    # Count insertions and deletions
    insertions = 0
    deletions = 0

    inserted_tokens = []
    deleted_tokens = []

    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            insertions += 1
            inserted_tokens.append(line[1:]) # exclude '+'
        elif line.startswith('-') and not line.startswith('---'):
            deletions += 1
            deleted_tokens.append(line[1:]) # exclude '-'

    return insertions, deletions, inserted_tokens, deleted_tokens