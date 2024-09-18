import tkinter as tk
import json
import pandas as pd

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
        'CourseCode': {'dtype': str, 'required': True},
        'SID': {'dtype': str, 'required': True},
        'TermOrder': {'dtype': int, 'required': True},
        'CreditHours': {'dtype': int, 'required': False},
        'FinalGrade': {'dtype': str, 'required': False},
        'FinalGradeN': {'dtype': int, 'required': False}
    }
    
    return field_info
