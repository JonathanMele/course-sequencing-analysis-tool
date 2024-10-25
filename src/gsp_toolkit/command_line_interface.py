from os import getcwd
from argparse import ArgumentParser, RawTextHelpFormatter
from sys import argv, exit
from webbrowser import open
from gsp_algorithm import execute_tool
import pandas as pd
from utils import preprocess_time, parse_dates, create_timegroup, get_timegroup_unit
from os import path, makedirs

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
    
    output_path = path.join(path.dirname(__file__), '..', '..', 'output')
    makedirs(path.dirname(output_path), exist_ok=True)

    parser = ArgumentParser(description="Run the Apriori algorithm on transaction data. Analyze course sequences to identify common paths taken by students.",
                                     formatter_class=RawTextHelpFormatter,
                                     epilog="""Examples:
    python command_line_interface.py -i data.csv -s 50,100 -c BISC,CHEM --m separate
    python command_line_interface.py -i data.csv -s 75 -c MATH,PHYS -m together -o results/

For more detailed examples, use --manual.""")

    parser.add_argument("-i", "--input", required=True, help="Input CSV file.")
    parser.add_argument("-s", "--support", required=True, help="Comma-separated support thresholds (e.g., 50,100).")
    parser.add_argument("-c", "--categories", required=False, help="Comma-separated categories (e.g., BIO,CHEM).")
    parser.add_argument("-m", "--mode", choices=['separate', 'together'], default='separate', help="Run 'separate' or 'together'. Default: separate.")
    parser.add_argument("-o", "--output", required=False, default=output_path, help="Output directory for results. Default: top-level output folder.")
    parser.add_argument("--concurrency", action='store_true', help="Enable concurrency and prompt to create TimeGroup if not present.")

    # Parse the rest of the arguments
    args = parser.parse_args()

    # Convert string inputs to the correct format
    support_thresholds = [float(threshold) for threshold in args.support.split(",")]

    if args.categories:
        categories = args.categories.split(",")
    else:
        categories = []

    df = pd.read_csv(args.input)

    if 'EventTime' not in df.columns:
        df, _ = preprocess_time(df)
    else:
        df = parse_dates(df, 'EventTime')

    # Check if concurrency is enabled
    if args.concurrency:
        if 'TimeGroup' not in df.columns:
            # Prompt for TimeGroup unit if it does not exist
            timegroup_unit = get_timegroup_unit()
            df = create_timegroup(df, 'EventTime', timegroup_unit)

    # Execute the tool with the provided arguments
    execute_tool(df, support_thresholds, categories, args.mode, args.output)

if __name__ == "__main__":
    main()
