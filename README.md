# pseudollm
Pseudonymization enhanced by OpenAI LLMs

This project provides a pipeline for pseudonymizing personally identifiable information (PII) in text files. It uses a combination of OpenAI's language models and Python to identify sensitive entities, generate culturally appropriate pseudonyms, and replace the original entities with pseudonyms while maintaining the text's natural flow.

## Features
* Automatically annotate PII (e.g., names, organizations, locations) in text files using `<to_pseudonym>` tags.
* Generate pseudonyms for tagged PII using OpenAI's GPT-based models.
* Replace tagged PII with pseudonyms in the text while maintaining consistency between them and context.
* Support for processing multiple files through a command-line interface (CLI).

## Project Structure
```graphql
.
├── LICENSE
├── README.md
├── pyproject.toml
└── src
    └── pseudollm
        ├── __init__.py
        ├── dict-to-schema.py   # utility script to create a JSON schema given a dictionary
        ├── main.py             # CLI script
        └── process.py          # Functions
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
Use the `tag` argument to annotate text files with <to_pseudonym> tags around PII:

```bash
pseudollm tag --input_files file1.txt file2.txt --output_dir ./annotated --example_file example_annotation.txt
```
Arguments:\
`--input_files`: Paths to input text files (can process multiple files).\ 
`--output_dir`: Directory to save annotated files.\
`--example_file`: Path to an example file containing sample annotations.\

2. Generate pseudonymized texts\
Use the `pseudonymize` argument to generate pseudonymized texts:

```bash
pseudollm pseudonymize --input_files ./annotated/*.txt --output_dir ./pseudonymized
```
Arguments:\
--input_files: Path to the annotated text files (can process multiple files).\
--output_dir: Path to the directory where to save the pseudonymized file.\

### Example Workflow
Input Text (`file1.txt`):\
`Dear John Smith, we are pleased to offer you a role at ACME Corp located in New York.`

Annotated Output (`annotated/file1.txt`):\
`Dear <to_pseudonym>John Smith</to_pseudonym>, we are pleased to offer you a role at <to_pseudonym>ACME Corp</to_pseudonym> located in <to_pseudonym>New York</to_pseudonym>.`

Pseudonymized Output (`pseudonymized/file1.txt`):\
`Dear Michael Carter, we are pleased to offer you a role at TechNova located in Silverlake.`

### Technical Details

**Annotation**: Uses OpenAI gpt-4o-mini to analyze text and tag PII with `<to_pseudonym>` markers.

**Pseudonym Generation**: Processes all PII in a text in a single prompt to maintain consistency across related entities. Returns a JSON schema with PII (original entities) and pseudonym (generated pseudonyms) arrays.

**Replacement**: Replaces all occurrences of `<to_pseudonym>{entity}</to_pseudonym>` with the corresponding pseudonym from the generated JSON schema.

## Known Issues
* Case Sensitivity: Entity replacement is case-sensitive.
* Token Limitations: OpenAI models have token limits. You can increase token limits by editing the related functions.

## Future Enhancements
* add `max_tokens` and `model` as parameters of the functions and options in the CLI.
* support also other models (e.g., open source models)

## Contributing
Fork this repository.
Create a feature branch: `git checkout -b feature-name`.
Commit your changes: `git commit -m "Add feature-name"`.
Push to your branch: `git push origin feature-name`.
Open a pull request.

## License
This project is licensed under the MIT License. See LICENSE for details.