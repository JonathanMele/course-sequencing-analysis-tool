import tkinter as tk
from dateutil import parser
import json
import pandas as pd
import numpy as np
import dateparser
from hashlib import md5
from os import path, makedirs

# A class to create ToolTips
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

    def showtip(self):
        # Method to show tooltip on hover
        self.tooltip_window = tk.Toplevel(self.widget)
        tooltip_label = tk.Label(self.tooltip_window, text=self.text)
        tooltip_label.pack()

        self.tooltip_window.overrideredirect(True)

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window.geometry(f"+{x}+{y}")

    def hidetip(self):
        # Method to hide tooltip when not hovering
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def save_to_folder(df, folder_path, file_name):
    makedirs(folder_path, exist_ok=True)
    df.to_csv(path.join(folder_path, file_name), index=False)
    return df

# Functions to process data
def filter_and_export_to_csv(data_dict, min_support, total_transactions, file_name):
    """
    Filters and exports the provided data to a CSV file.

    Args:
        data_dict (dict): Dictionary containing the data to be exported.
        min_support (float): Minimum support threshold.
        total_transactions (int): Total number of transactions in the data.
        file_name (str): Name of the CSV file to which data will be exported.

    Returns:
        dict: A dictionary containing the counts of itemsets.
    """
    data_df = pd.DataFrame(data_dict)
   
    for column in data_df:
        data_df.drop(data_df[data_df[column] < min_support].index, inplace=True)
    
    itemset_counts = data_df.count().to_dict()
    data_df['Count %'] = (data_df.sum(axis=1) / total_transactions) * 100
    data_df.to_csv(file_name)
    
    return itemset_counts

def export_summary_to_file(single_item_count, itemset_count, total_transactions, elapsed_time, file_path):
    """
    Exports a summary of the results to a text file.

    Args:
        single_item_count (dict): Dictionary containing the count of single items.
        itemset_count (dict): Dictionary containing the count of itemsets of different sizes.
        total_transactions (int): Total number of transactions in the data.
        elapsed_time (float): Time taken to run the algorithm.
        file_path (str): Path to the text file where the summary will be written.

    Returns:
        None
    """
    with open(file_path, 'a') as file:
        file.write("===" * 20 + "\n")
        file.write(json.dumps(single_item_count))
        file.write("\n\n")
        file.write(json.dumps(itemset_count))
        file.write("\n\n")
        file.write(f"Transaction #: {total_transactions}")
        file.write("\n\n")
        file.write(f"--- {elapsed_time} seconds ---\n\n")

def get_data_dictionary():
    """
    Returns a dictionary of the data used in the tool, including dtype
    and whether its optional.
    
    Returns:
        dict: Dictionary containing data information.
    """
    field_info = {
        'Item': {'dtype': str, 'required': True},
        'ID': {'dtype': str, 'required': True},
        'EventTime': {'dtype': int, 'required': True},
        'CreditHours': {'dtype': int, 'required': False},
        'FinalGrade': {'dtype': str, 'required': False},
        'FinalGradeN': {'dtype': int, 'required': False}
    }
    
    return field_info

def generate_hash(input_string):
    """Generate a unique hash from an input string."""
    return md5(input_string.encode()).hexdigest()

def create_timegroup(df, time_column, timegroup_unit):
    """
    Create a TimeGroup column based on the specified timegroup unit.

    Args:
        df (pd.DataFrame): The dataframe containing the time column.
        time_column (str): The column name containing the time data (must be in datetime format).
        timegroup_unit (str): The unit of time to group by (e.g., 'Y' for Year, 'M' for Month, 'W' for Week, 'Q' for Quarter).

    Returns:
        pd.DataFrame: The dataframe with the new 'TimeGroup' column added.
    """
    if timegroup_unit == 'Y':
        df['TimeGroup'] = df[time_column].dt.year
    elif timegroup_unit == 'M':
        df['TimeGroup'] = df[time_column].dt.month
    elif timegroup_unit == 'W':
        df['TimeGroup'] = df[time_column].dt.isocalendar().week
    elif timegroup_unit == 'Q':
        df['TimeGroup'] = df[time_column].dt.quarter
    else:
        raise ValueError(f"Unsupported time group unit: {timegroup_unit}")
    
    save_path = path.join(path.dirname(__file__), '..', '..', 'data')
    df = save_to_folder(df, save_path, 'preprocessed_data.csv')
    
    return df

def detect_date_columns_with_dateparser(df):
    """
    Use `dateparser` to detect columns that contain date-like values.
    """
    exclude_columns = ['ID', 'id', 'Item']
    date_columns = []

    df_copy = df.copy()
    
    for col in df_copy.columns:
        if col not in exclude_columns:
            # Try parsing the first 10 non-null values in each column using `dateparser`
            if df_copy[col].dropna().head(10).apply(lambda x: dateparser.parse(str(x)) is not None).any():
                date_columns.append(col)
    
    return date_columns

def parse_dates(df, column_name):
    """
    Parse dates dynamically using `dateparser`.
    Handles various formats such as slashes, hyphens, and different day-month orders.
    """
    # Replace empty strings with NaN for clean parsing
    df[column_name] = df[column_name].replace('', np.nan)

    # Parse the dates dynamically using `dateparser` to handle all formats
    df['EventTime'] = df[column_name].apply(lambda x: dateparser.parse(x) if pd.notna(x) else np.nan)
    df['EventTime'] = pd.to_datetime(df['EventTime'])

    # Check if any values remain unparsed (NaT) and log them
    if df['EventTime'].isna().sum() > 0:
        print(f"Warning: Some dates could not be parsed in the column {column_name}.")
    
    return df

def get_ordering(unique_values, gui=False):
    """
    Prompt the user to specify the order of the unique values in the column.

    Args:
        unique_values (list): List of unique values in the column.
        gui (bool): Whether to prompt the user in the tkinter GUI.

    Returns:
        list: A list of ordered values (e.g., ['Spring', 'Fall']).
    """
    if gui:
        from tkinter import Tk
        root = Tk()
        root.withdraw()  # Hide the root window
        
        # Popup message to explain what the user should do
        message = f"Please enter the order of the following values, separated by commas, from earliest to latest:\n{unique_values}"
        
        # Ask the user to provide the order
        ordering_input = tk.simpledialog.askstring("Specify Order", message)
        
        # Convert input into a list of ordered values
        ordered_values = [val.strip() for val in ordering_input.split(',')]
    else:
        # Prompt in CLI
        print(f"Please specify the order of the following values, separated by commas, from earliest to latest:\n{unique_values}")
        ordering_input = input("Enter the order: ")
        
        # Convert input into a list of ordered values
        ordered_values = [val.strip() for val in ordering_input.split(',')]

    return ordered_values

def get_timegroup_unit(gui=False):
    if gui:
        from tkinter import Tk
        root = Tk()
        root.withdraw()
        message = "Please specify the time grouping unit (e.g., 'Y' for Year, 'M' for Month, 'W' for Week, 'Q' for Quarter [Semester])."
        timegroup_unit = tk.simpledialog.askstring("Specify Time Group Unit", message)
    else:
        print("Please specify the time grouping unit (e.g., 'Y', 'M', 'W', 'Q').")
        timegroup_unit = input("Enter the time unit: ")
    return timegroup_unit.strip().upper()

def preprocess_time(df, concurrency=False, gui=False):
    # hardcoded column names
    potential_date_columns = [col for col in df.columns if 'year' in col.lower() or 'semester' in col.lower()]
    # potential column names
    computed_date_columns = detect_date_columns_with_dateparser(df)
    
    potential_date_columns = list(set(potential_date_columns + computed_date_columns))
    
    if len(potential_date_columns) == 0:
        raise ValueError("No date-like columns detected in the dataset.")
    
    if len(potential_date_columns) > 1:
        if gui:
            from tkinter import Tk
            root = Tk()
            root.withdraw()

            message = (f"Multiple columns were detected that may represent time-based information: {potential_date_columns}.\n\n"
                       "Please select the column that represents the time or date you want to use for ordering events.")
            
            column_name = tk.simpledialog.askstring("Select Time Column", message)
            
            if column_name not in df.columns:
                raise ValueError(f"Column '{column_name}' is not in the dataset.")
        else:
            print(f"Multiple columns were detected that may represent time-based information: {potential_date_columns}")
            column_name = input("Type the column name: ")
            
            if column_name not in df.columns:
                raise ValueError(f"Column '{column_name}' is not in the dataset.")
    else:
        column_name = potential_date_columns[0]

    # Handle columns that do not contain numbers (e.g., 'Spring', 'Fall') not just objects
    if column_name.lower() == 'semester':
        unique_values = df[column_name].unique()
        ordered_values = get_ordering(unique_values, gui=gui)  # Prompt user for ordering (e.g., ['Spring', 'Summer', 'Fall'])
        num_unique_values = len(ordered_values)
        month_step = 12 // num_unique_values  # Distribute evenly across 12 months
        value_to_month = {val: (i * month_step + 1) for i, val in enumerate(ordered_values)}
        
        if 'Year' in df.columns:
            df['EventTime'] = df.apply(lambda row: pd.Timestamp(f"{row['Year']}-{value_to_month.get(row[column_name], 1)}-01"), axis=1)
        else:
            default_year = 2000
            df['EventTime'] = df.apply(lambda row: pd.Timestamp(f"{default_year}-{value_to_month.get(row[column_name], 1)}-01"), axis=1)
    
    else:
        # Apply the date parsing using `dateparser` for regular date columns
        df = parse_dates(df, column_name)

        # Final check: Ensure some valid dates were parsed
        if df['EventTime'].isna().all():
            raise ValueError("Unable to parse any valid dates from the specified columns.")

    save_path = path.join(path.dirname(__file__), '..', '..', 'data')
    df = save_to_folder(df, save_path, 'preprocessed_data.csv')

    return df, save_path + '/preprocessed_data.csv'