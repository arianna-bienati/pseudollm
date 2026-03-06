import json
import ollama
import re

def num_tokens_from_messages(messages):
    """Rough token estimate (4 chars ≈ 1 token)."""
    total_chars = sum(len(v) for msg in messages for v in msg.values())
    return total_chars // 4

def extract_thinking(response_text, logger=None):
    """Strip <think>...</think> block from response, optionally logging it."""
    think_match = re.search(r'<think>(.*?)</think>', response_text, re.DOTALL)
    if think_match and logger:
        logger.info(f"[THINKING]\n{think_match.group(1).strip()}")
    return re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()

def annotate_pii_ollama(input_file, output_file, example_file, model="deepseek-r1:14b", logger=None):
    with open(input_file, 'r') as f:
        file_content = f.read()
    with open(example_file, 'r') as ex:
        example = ex.read()

    messages = [
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

    prompt_tokens = num_tokens_from_messages(messages)

    response = ollama.chat(
        model=model,
        messages=messages,
        options={
            "temperature": 0,
            "num_predict": prompt_tokens * 2
        }
    )

    result = extract_thinking(response.message.content, logger)

    with open(output_file, 'w') as out_f:
        out_f.write(result)


def generate_pseudonyms_ollama(entities, model="deepseek-r1:14b"):
    messages = [
        {
            "role": "system",
            "content": "You are a pseudonym generator. You will be provided with a list of personally identifiable information (PII). Your task is to assign suitable pseudonyms to each of the entities, using the pseudonym field. Ensure the pseudonyms match the tone and cultural context of the entities, contain the same number of words, and are consistent within the set. Respond ONLY with a JSON object with two arrays: 'PII' (original entities) and 'pseudonym' (corresponding pseudonyms). No markdown, no explanation."
        },
        {
            "role": "user",
            "content": "\n".join(entities)
        }
    ]

    prompt_tokens = num_tokens_from_messages(messages)

    response = ollama.chat(
        model=model,
        messages=messages,
        format="json",
        options={
            "temperature": 0.8,
            "num_predict": prompt_tokens * 2
        }
    )

    pseudonym_map = json.loads(response.message.content)
    return pseudonym_map