from os import getcwd
from argparse import ArgumentParser, RawTextHelpFormatter
from sys import argv, exit
from webbrowser import open
from gsp_algorithm import execute_tool
import pandas as pd
from utils import preprocess_time

def print_introduction():
    introduction_text = """
    ***********************************************************
    Welcome to the CLI for Course Sequence Analysis Tool (CSAT)
    ***********************************************************
    
    This tool allows you to analyze course sequences using Apriori-based
    Generalized Sequential Pattern (GSP) algorithm. Specify input parameters
    to customize your analysis.

    For detailed help on each parameter, use the --help option.
    For usage examples, see the 'Examples' section in the --help output.
    
    Access the full manual with --manual.
    """
    print(introduction_text)

def open_manual():
    manual_url = "https://docs.google.com/document/d/1yb6dg26jO_m0ir80vgfoN9ED0RF3bohMhJi0B3aig8w/edit?usp=sharing"
    print(f"Opening the manual: {manual_url}")
    open(manual_url)

def main():
    if "--manual" in argv:
        open_manual()
        exit(0)

    if len(argv) == 1:
        print_introduction()
        exit(1)

    parser = ArgumentParser(description="Run the Apriori algorithm on transaction data. Analyze course sequences to identify common paths taken by students.",
                                     formatter_class=RawTextHelpFormatter,
                                     epilog="""Examples:
    python gui.py --input_file data.csv --support_thresholds 50,100 --categories BISC,CHEM --run_mode separate
    python gui.py --input_file data.csv --support_thresholds 75 --categories MATH,PHYS --run_mode together --output_dir results/

For more detailed examples, use --manual.""")

    parser.add_argument("--input_file", required=True, help="Path to the input CSV file. Ensure the file is in CSV format.")
    parser.add_argument("--support_thresholds", required=True, help="Comma-separated list of support thresholds. Example: 50,100")
    parser.add_argument("--categories", required=False, help="Comma-separated list of categories. For departments, this is like BIO,CHEM.")
    parser.add_argument("--run_mode", choices=['separate', 'together'], required=False, default='separate', help="Run mode: 'separate' for analyzing departments separately, 'together' for combined analysis. Defaults to 'separate'.")
    parser.add_argument("--output_dir", required=False, default=getcwd(), help="Directory to store output results. Defaults to current working directory if not specified.")

    # Parse the rest of the arguments
    args = parser.parse_args()

    # Convert string inputs to the correct format
    support_thresholds = [float(threshold) for threshold in args.support_thresholds.split(",")]

    if args.categories:
        categories = args.categories.split(",")
    else:
        categories = []

    df = pd.read_csv(args.input_file)
    cleaned_df = preprocess_time(df)

    # Execute the tool with the provided arguments
    execute_tool(cleaned_df, support_thresholds, categories, args.run_mode, args.output_dir)

if __name__ == "__main__":
    main()
