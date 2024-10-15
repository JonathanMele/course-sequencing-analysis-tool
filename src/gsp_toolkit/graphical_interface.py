import os
import csv
import webbrowser
import threading
import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
from gsp_algorithm import execute_tool
from data_processing import data_cleanup
from utils import ToolTip, get_data_dictionary, preprocess_time, get_timegroup_unit, create_timegroup, parse_dates
from os import path, makedirs

class GSPTool:
    def __init__(self, root):
        self.root = root
        self.file_df = None
        self.results = None
        self.concurrent_var = tk.IntVar()  # Future option for toggling concurrency
        output_path = path.join(path.dirname(__file__), '..', '..', 'output')
        makedirs(path.dirname(output_path), exist_ok=True)
        self.output_directory = output_path
        self.input_file_name = tk.StringVar()
        self.min_supports = []
        self.categories = set()
        self.select_all_var = tk.IntVar()
        self.run_mode_var = tk.StringVar(value="together")
        self.root.title("Sequencing Analysis Tool")
        self.category_label_str = "Category"
        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.setup_gui()

    def setup_gui(self):
        tk.Label(self.root, text="Input File Name:").grid(row=0, column=0, sticky=tk.W)
        input_file_name_entry = tk.Entry(self.root, textvariable=self.input_file_name)
        input_file_name_entry.grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_file).grid(row=0, column=2)
        self.bind_tooltip_events(input_file_name_entry, "Enter the path of the input file containing transaction data.")

        tk.Label(self.root, text="Minimum Support(s):").grid(row=1, column=0, sticky=tk.W)
        self.min_supports_entry = tk.Entry(self.root)
        self.min_supports_entry.grid(row=1, column=1)
        self.bind_tooltip_events(self.min_supports_entry, "Enter the minimum support(s) as comma-separated values.")

        # Concurrency checkbox
        self.concurrent_checkbox = tk.Checkbutton(self.root, text="Enable Concurrency", variable=self.concurrent_var, command=self.toggle_concurrency)
        self.concurrent_checkbox.grid(row=2, column=0, sticky=tk.W)

        # Dynamically set the label to "Departments" for course-related data or "Category" for general data
        self.category_label = tk.Label(self.root, text=self.category_label_str + "(s):")
        self.category_label.grid(row=3, column=0, sticky=tk.W)

        self.categories_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.categories_listbox.grid(row=3, column=1)
        self.categories_listbox.bind('<<ListboxSelect>>', self.update_radio_buttons_state)
        self.bind_tooltip_events(self.categories_listbox, f"Select one or more {self.category_label_str.lower()}(s) for the GSP algorithm.")

        button_frame = tk.Frame(self.root)
        button_frame.grid(row=3, column=2, padx=10)

        self.select_all_checkbox = tk.Checkbutton(button_frame, text="Select All", variable=self.select_all_var, command=self.select_all_categories)
        self.select_all_checkbox.pack(side=tk.TOP, pady=2)

        self.run_mode_radio_together = tk.Radiobutton(button_frame, text="Run Together", variable=self.run_mode_var, value="together")
        self.run_mode_radio_together.pack(side=tk.TOP, pady=2)
        self.run_mode_radio_together.config(state=tk.DISABLED)

        self.run_mode_radio_separate = tk.Radiobutton(button_frame, text="Run Separately", variable=self.run_mode_var, value="separate")
        self.run_mode_radio_separate.pack(side=tk.TOP, pady=2)
        self.run_mode_radio_separate.config(state=tk.DISABLED)

        self.hide_category_widgets()

        tk.Label(self.root, text="Output Directory:").grid(row=4, column=0, sticky=tk.W)
        self.output_directory_label = tk.Label(self.root, text=self.output_directory)
        self.output_directory_label.grid(row=4, column=1)
        self.bind_tooltip_events(self.output_directory_label, "Specify the output directory for the algorithm results.")

        tk.Button(self.root, text="Browse", command=self.set_output_directory).grid(row=4, column=2)
        tk.Button(self.root, text="Run GSP", command=self.run_gsp).grid(row=5, column=0, pady=10)
        tk.Button(self.root, text="Help", command=self.open_web).grid(row=5, column=2)

        self.run_status_label = tk.Label(self.root, text="")
        self.run_status_label.grid(row=5, column=1)

        self.root.mainloop()
    
    def hide_category_widgets(self):
        """Hide category/department-related widgets."""
        self.category_label.grid_remove()
        self.categories_listbox.grid_remove()
        self.select_all_checkbox.grid_remove()
        self.run_mode_radio_together.grid_remove()
        self.run_mode_radio_separate.grid_remove()

    def show_category_widgets(self):
        """Show category/department-related widgets."""
        self.category_label.grid()
        self.categories_listbox.grid()
        self.select_all_checkbox.grid()
        self.run_mode_radio_together.grid()
        self.run_mode_radio_separate.grid()

    def toggle_concurrency(self):
        if self.concurrent_var.get():
            # If concurrency is selected, ensure that TimeGroup is present
            if 'TimeGroup' not in self.file_df.columns:
                self.prompt_timegroup()
    
    def prompt_timegroup(self):
        """Prompt the user to create the TimeGroup column if not already present."""
        timegroup_unit = get_timegroup_unit(gui=True)

        # Call the utility function to create the TimeGroup
        self.file_df = create_timegroup(self.file_df, 'EventTime', timegroup_unit)

    def bind_tooltip_events(self, widget, text):
        tooltip = ToolTip(widget, text)
        widget.bind("<Enter>", lambda event: tooltip.showtip())
        widget.bind("<Leave>", lambda event: tooltip.hidetip())

    def open_web(self):
        webbrowser.open('https://docs.google.com/document/d/1yb6dg26jO_m0ir80vgfoN9ED0RF3bohMhJi0B3aig8w/edit?usp=sharing')

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.input_file_name.set(file_path)

        df = pd.read_csv(file_path)

        # Preprocess the time if 'EventTime' does not exist
        if 'EventTime' not in df.columns:
            self.file_df, file_path = preprocess_time(df, gui=True)
            self.input_file_name.set(file_path)
        else:
            self.file_df = parse_dates(df, 'EventTime')
        
        self.validate_categories(file_path)

    def validate_categories(self, file_path):
        self.categories.clear()
        if not file_path:
            return

        with open(file_path, "r") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            fieldnames = csv_reader.fieldnames

            # Detect if the file is course-related (uses "Department") or generalized (uses something else)
            if "Department" in fieldnames:
                self.category_label.config(text="Department(s):")
                self.show_category_widgets()
            elif "Category" in fieldnames:
                self.category_label.config(text="Category(s):")
                self.show_category_widgets()
            else:
                self.hide_category_widgets()

            for row in csv_reader:
                # Handle course data (departments) or general data (categories)
                if "Department" in row:
                    category = row["Department"]
                elif "Category" in row:
                    category = row["Category"]
                else:
                    # Extract from CourseCode or a general item code
                    category = ''.join(filter(str.isalpha, row.get("CourseCode", row.get("Item", ""))))

                if category not in self.categories:
                    self.categories.add(category)

        sorted_departments = sorted(self.categories)
        self.categories_listbox.delete(0, tk.END)
        for category in sorted_departments:
            self.categories_listbox.insert(tk.END, category)

    def update_radio_buttons_state(self, event=None):
        selected_categories = self.categories_listbox.curselection()
        if len(selected_categories) > 1:
            self.run_mode_radio_together.config(state=tk.NORMAL)
            self.run_mode_radio_separate.config(state=tk.NORMAL)
        else:
            self.run_mode_radio_together.config(state=tk.DISABLED)
            self.run_mode_radio_separate.config(state=tk.DISABLED)

    def select_all_categories(self):
        if self.select_all_var.get():
            self.categories_listbox.select_set(0, tk.END)
        else:
            self.categories_listbox.selection_clear(0, tk.END)
        self.update_radio_buttons_state()

    def set_output_directory(self):
        self.output_directory = filedialog.askdirectory()
        if not self.output_directory:
            self.output_directory_label.config(text="Not specified.")
        else:
            self.output_directory_label.config(text=self.output_directory)

    def run_gsp(self):
        def target():
            self.run_status_label.config(text="Running tool ..")
            self.progress.grid(row=6, column=0, columnspan=3, sticky=tk.EW)
            self.progress.start()

            try:
                self.results = execute_tool(self.file_df, min_supports, selected_categories, run_mode_var, self.output_directory)
            finally:
                self.progress.stop()
                self.progress.grid_forget()
                self.run_status_label.config(text="GSP finished running.\nVerify results in 'Output Directory'")

        selected_categories = [self.categories_listbox.get(i) for i in self.categories_listbox.curselection()]
    
        print(f"Selected categories: {selected_categories}")
        print(f"All categories: {self.categories}")

        if not selected_categories and len(self.categories) != 0:
            tk.messagebox.showwarning("No categories selected", "Please select at least one category to run GSP.")
        elif not self.min_supports_entry.get():
            tk.messagebox.showwarning("No minimum supports", "Please specify at least one minimum support value.")
        else:
            min_supports_str = self.min_supports_entry.get()
            min_supports = [int(s) for s in min_supports_str.split(",")]
            run_mode_var = self.run_mode_var.get()
            threading.Thread(target=target).start()

if __name__ == "__main__":
    root = tk.Tk()
    GSPTool(root)
