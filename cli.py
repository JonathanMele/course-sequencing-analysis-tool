import argparse
import sys
import webbrowser
from lab_code import execute_tool

def print_introduction():
    introduction_text = """
    ***********************************************************
    Welcome to the CLI for Course Sequence Analysis Tool (CSAT)
    ***********************************************************
    
    For detailed help on each parameter, use the --help option.
    For usage examples, see the examples section in the --help output.
    
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

    parser = argparse.ArgumentParser(description="Run the Apriori algorithm on transaction data.",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog="For more information and examples, visit our project page or use --manual.")
    parser.add_argument("--input_file", required=True, help="Path to the input CSV file.\nTooltip: Ensure the file is in CSV format.")
    parser.add_argument("--support_thresholds", required=True, help="Comma-separated list of support thresholds.\nTooltip: Example - 0.1,0.2")
    parser.add_argument("--departments", required=True, help="Comma-separated list of department codes.\nTooltip: Include departments like Math,Science.")
    parser.add_argument("--run_mode", choices=['separate', 'together'], required=True, help="Run mode: 'separate' or 'together'.\nTooltip: Choose based on data processing preference.")
    parser.add_argument("--output_dir", required=True, help="Directory to store the output results.\nTooltip: Specify a directory path.")

    # parse the rest of the arguments
    args = parser.parse_args()

    # convert string inputs to the correct format
    support_thresholds = [float(threshold) for threshold in args.support_thresholds.split(",")]
    departments = args.departments.split(",")

    # execute the tool with the provided arguments
    execute_tool(args.input_file, support_thresholds, departments, args.run_mode, args.output_dir)

if __name__ == "__main__":
    main()
