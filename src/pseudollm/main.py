import argparse
import argcomplete
from pathlib import Path

from tqdm.auto import tqdm

import pseudollm.process as process

def _tag(args):
	# Create output dir if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Use tqdm for progress tracking if there are multiple files
    for input_file in tqdm(args.input_files, desc="Tagging files"):
        input_path = Path(input_file).resolve()
        output_file = output_dir / f"{input_path.stem}_tagged{input_path.suffix}"
        example_file = Path(args.example_file).resolve()
        process.annotate_pii(input_path, output_file, example_file)
        print(f"Annotated and saved to {output_file}")

def _pseudonymize(args):
    logger = process.setup_logger()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    for input_file in tqdm(args.input_files, desc="Pseudonymizing files"):
        input_path = Path(input_file).resolve()
        logger.info(f"\nProcessing file: {input_path.name}")

        with open(input_file, 'r') as f:
            file_content = f.read()
        
        matches = process.extract_tags(file_content)
        logger.info(f"Found {len(matches)} entities to pseudonymize")
        
        pseudonym_dict = process.generate_pseudonyms(matches)
        pseudonym_text, replacements_made = process.pseudonymization(file_content, pseudonym_dict, logger)
        logger.info(f"Total replacements: {replacements_made}")

        if len(matches) != replacements_made:
            logger.warning(f"⚠️ Mismatch: Expected {len(matches)} replacements, made {replacements_made}")

        output_file = output_dir / f"{input_path.stem}_pseudonym{input_path.suffix}"
        with open(output_file, 'w') as out_f:
            out_f.write(pseudonym_text)

        print(f"Pseudonymized and saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Pseudonymize Personally Identifiable Information using OpenAI LLMs",
        add_help=True)
    
    argcomplete.autocomplete(parser)

    subparsers = parser.add_subparsers(title="actions", dest="actions")
    
    parser_tag = subparsers.add_parser('tag',
        description='Tag Personally Identifiable Information in texts',
        help='Tag Personally Identifiable Information in texts')
    
    parser_tag.add_argument("-o", "--output_dir",
        type=str,
        default=".",
        help="Output directory. Default: Current directory.")
    
    parser_tag.add_argument("-i", "--input_files",
        type=str,
        nargs="+",
        required=True,
        help="Input text files.")
    
    parser_tag.add_argument("-ex", "--example_file",
        type=str,
        help="Input example file.")
    
    parser_tag.set_defaults(func=_tag)

    parser_pseudonymize = subparsers.add_parser('pseudonymize',
        description='Pseudonymize Personally Identifiable Information in texts',
        help='Pseudonymize Personally Identifiable Information in texts')
    
    parser_pseudonymize.add_argument("-o", "--output_dir",
        type=str,
        default=".",
        help="Output directory. Default: Current directory.")
    
    parser_pseudonymize.add_argument("-i", "--input_files",
        type=str,
        nargs="+",
        required=True,
        help="Input text files.")
    
    parser_pseudonymize.set_defaults(func=_pseudonymize)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_usage()
        exit(1)

    args.func(args)

if __name__ == "__main__":
    main()