import argparse
import sys
import os
import webbrowser
from lab_code import execute_tool

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
    webbrowser.open(manual_url)

def main():
    if "--manual" in sys.argv:
        open_manual()
        sys.exit(0)

    if len(sys.argv) == 1:
        print_introduction()
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Run the Apriori algorithm on transaction data. Analyze course sequences to identify common paths taken by students.",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog="""Examples:
    python gui.py --input_file data.csv --support_thresholds 50,100 --departments BISC,CHEM --run_mode separate
    python gui.py --input_file data.csv --support_thresholds 75 --departments MATH,PHYS --run_mode together --output_dir results/

For more detailed examples, use --manual.""")

    parser.add_argument("--input_file", required=True, help="Path to the input CSV file. Ensure the file is in CSV format.")
    parser.add_argument("--support_thresholds", required=True, help="Comma-separated list of support thresholds. Example: 50,100")
    parser.add_argument("--departments", required=True, help="Comma-separated list of department codes. Include departments like BIO,CHEM.")
    parser.add_argument("--run_mode", choices=['separate', 'together'], required=False, default='separate', help="Run mode: 'separate' for analyzing departments separately, 'together' for combined analysis. Defaults to 'separate'.")
    parser.add_argument("--output_dir", required=False, default=os.getcwd(), help="Directory to store output results. Defaults to current working directory if not specified.")

    # Parse the rest of the arguments
    args = parser.parse_args()

    # Convert string inputs to the correct format
    support_thresholds = [float(threshold) for threshold in args.support_thresholds.split(",")]
    departments = args.departments.split(",")

    # Execute the tool with the provided arguments
    execute_tool(args.input_file, support_thresholds, departments, args.run_mode, args.output_dir)

if __name__ == "__main__":
    main()
