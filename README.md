# pseudollm
Pseudonymization enhanced by OpenAI LLMs

This project provides a pipeline for pseudonymizing personally identifiable information (PII) in text files. It uses a combination of OpenAI's language models and Python to identify sensitive entities, generate culturally appropriate pseudonyms, and replace the original entities with pseudonyms while maintaining the text's natural flow.

## Features
* Automatically annotate PII (e.g., names, organizations, locations) in text files using `<to_pseudonym>` tags.
* Generate pseudonyms for tagged PII using OpenAI's GPT-based models.
* Replace tagged PII with pseudonyms in the text while maintaining consistency between them and context.
* Support for processing multiple files through a command-line interface (CLI).

### New features 27/11/2024
* During the annotation process the 'type' of entity is also specified using the tag `<to_pseudodym type = "value">`. Possible entity types are PER (person), LOC (location), ORG (organization) and MISC (miscellanea). This simple ontology is taken from [packages with 4 entity types in Stanza](https://stanfordnlp.github.io/stanza/ner_models.html).
* This information can be used with the `anonymize` subparser to obtain a text pseudonymized with more general placeholders. Useful when a stronger pseudonymization is needed and there is no need to maintain the text's natural flow.

### New feature 21/01/2025
* You can now compare insertions and deletions in the original vs. the pseudonymized text using the `validate` argument. It uses difflib with a simple tokenization under the hood.

## Project Structure
```graphql
.
├── LICENSE
├── README.md
├── pyproject.toml
├── src
│   └── pseudollm
│       ├── __init__.py         
│       ├── dict-to-schema.py   # Utility script to create a JSON schema given a dictionary
│       ├── main.py             # CLI script
│       └── process.py          # Functions
└── test_data                   # All you need to test the package:
    ├── example_tagged.txt      # An hand-tagged text that serves as an example for tagging
    └── test.txt                # AI generated text with plenty of Personally Identifiable Information
```

## Installation
Clone this repository:
```bash
git clone https://github.com/arianna-bienati/pseudollm.git
cd pseudollm
```
Create a virtual environment and activate it
```bash
python -m venv .venv
source .venv/bin/activate
```
Install package in development mode
```bash
pip install -e .
```
Obtain an OpenAI API key from OpenAI and set it as an environment variable:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

## Usage

1. Annotate PII in text\
Use the `tag` argument to annotate text files with <to_pseudonym type = 'value'> tags around PII:

```bash
pseudollm tag -i ./test_data/en_test.txt -o ./test_data -ex ./test_data/example_tagged.txt 
```
Arguments:
* `--input_files`: Paths to input text files (can process multiple files). 
* `--output_dir`: Directory to save annotated files. Default is current directory.
* `--example_file`: Path to an example file containing sample annotations.

> [!TIP]
> Manually check the output of this first step!

2. Generate pseudonymized texts\
Use the `pseudonymize` argument to generate pseudonymized texts:

```bash
pseudollm pseudonymize -i ./test_data/en_test_tagged.txt -o ./test_data
```
Arguments:
* `--input_files`: Path to the annotated text files (can process multiple files).
* `--output_dir`: Path to the directory where to save the pseudonymized file.

3. OR pseudonymize texts with NER tags\
Use the `ner_pseudonymize` argument to replace Personally Identifiable Information with Named Entities tags:

```bash
pseudollm ner_pseudonymize -i ./test_data/en_test_tagged.txt -o ./test_data
```

> [!NOTE]  
> The package does not provide an integrated pipeline of the tagging > pseudonymizing/anonymizing steps as a nudge to do a quality check on the output of the annotation step.

4. Validate the output
Use the `validate` argument to check the replacements. The output tells you whether the number of insertions and deletions is the same and lists all insertions and deletions.

```bash
pseudollm validate -1 ./test_data/en_test.txt -2 ./test_data/en_test_tagged_pseudonym.txt
```

### Example Workflow
Input Text:\
`Dear John Smith, we are pleased to offer you a role at ACME Corp located in New York.`

Tagged Output:\
`Dear <to_pseudonym type = "PER">John Smith</to_pseudonym>, we are pleased to offer you a role at <to_pseudonym type = "ORG">ACME Corp</to_pseudonym> located in <to_pseudonym type = "LOC">New York</to_pseudonym>.`

Pseudonymized Output:\
`Dear Michael Carter, we are pleased to offer you a role at TechNova located in Silverlake.`

Pseudonymized with NER Output:\
`Dear [PER], we are pleased to offer you a role at [ORG] located in [LOC].`

## Technical Details

**Token count**: Uses the `tiktoken` package to count the number of tokens required to perform the tagging and the pseudonymization task (with a margin of 200 tokens) and sets this estimate for the `max_token` parameter.

**Annotation**: Uses OpenAI gpt-4o-mini to tag the PII with `<to_pseudonym type = "value">` markers.

**Pseudonym Generation**: Uses OpenAI gpt-4o to process all PII in a text and returns a JSON schema with PII (original entities) and pseudonym (generated pseudonyms) arrays. All PII are given in a single prompt to maintain consistency across related entities.

**Replacement**: Replaces all occurrences of `<to_pseudonym type = "value">{entity}</to_pseudonym>` with the corresponding pseudonym from the generated JSON schema.\
OR replaces all occurrences of `<to_pseudonym type = "value">{entity}</to_pseudonym>` with the value given in the attribute 'type'.

## Known Issues
* Case Sensitivity: Entity replacement is case-sensitive.
* Token Limitations: OpenAI models have token limits. The token limit for the models set as default (gpt-4o-mini and gpt-4o) is 16,384 tokens. If you know you have texts longer than this limit, consider splitting them. Use the `tiktoken` library to get an estimate.

## Future Enhancements
* add `max_tokens` and `model` as parameters of the functions and options in the CLI. :white_check_mark: done on 27/11/2024
* support also other models (e.g., open source models)
* systematically evaluate the tool

## Contributing
Fork this repository.\
Create a feature branch: `git checkout -b feature-name`.\
Commit your changes: `git commit -m "Add feature-name"`.\
Push to your branch: `git push origin feature-name`.\
Open a pull request.

## License
This project is licensed under the MIT License. See LICENSE for details.