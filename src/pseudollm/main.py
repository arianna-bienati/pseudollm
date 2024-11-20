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
        print(f"Converted {input_file} to {output_file}")

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

    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_usage()
        exit(1)

    args.func(args)

if __name__ == "__main__":
    main()