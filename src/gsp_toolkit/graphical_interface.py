import os
import csv
import webbrowser
import threading
import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
from gsp_algorithm import execute_tool
from data_processing import data_cleanup
from utils import ToolTip, get_data_dictionary

# The main class of the application
class GSPTool:
    def __init__(self, root):
        self.root = root
        # Initialize all necessary instance variables
        self.results = None
        self.output_directory = os.getcwd()
        self.input_file_name = tk.StringVar()
        self.min_supports = []
        self.departments = set()
        self.select_all_var = tk.IntVar()
        self.run_mode_var = tk.StringVar(value="together")
        self.root.title("Course Sequencing Analysis Tool")
        # Initialize all necessary UI elements as None, they will be defined in setup_gui
        self.departments_listbox = None
        self.run_mode_radio_together = None
        self.run_mode_radio_separate = None
        self.output_directory_label = None
        self.run_status_label = None
        self.show_cleanup = False
        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.setup_gui()    # Run GUI setup

    def setup_gui(self):
        # Method to set up the user interface
        tk.Label(self.root, text="Input File Name:").grid(row=0, column=0, sticky=tk.W)
        input_file_name_entry = tk.Entry(self.root, textvariable=self.input_file_name)
        input_file_name_entry.grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_file).grid(row=0, column=2)
        if self.show_cleanup:
            tk.Button(self.root, bg="red", command=self.data_cleanup).grid(row=0 , column=3)

        self.bind_tooltip_events(input_file_name_entry, "Enter the path of the input file containing transaction data.")

        tk.Label(self.root, text="Minimum Support(s):").grid(row=1, column=0, sticky=tk.W)
        self.min_supports_entry = tk.Entry(self.root)
        self.min_supports_entry.grid(row=1, column=1)
        self.bind_tooltip_events(self.min_supports_entry, "Enter the minimum support(s) as comma-separated values.")

        tk.Label(self.root, text="Department(s):").grid(row=2, column=0, sticky=tk.W)
        self.departments_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.departments_listbox.grid(row=2, column=1)
        self.departments_listbox.bind('<<ListboxSelect>>', self.update_radio_buttons_state)
        self.bind_tooltip_events(self.departments_listbox, "Select one or more departments for which to run the GSP algorithm.")

        button_frame = tk.Frame(self.root)
        button_frame.grid(row=2, column=2, padx=10)

        select_all_checkbox = tk.Checkbutton(button_frame, text="Select All", variable=self.select_all_var, command=self.select_all_departments)
        select_all_checkbox.pack(side=tk.TOP, pady=2)

        self.run_mode_radio_together = tk.Radiobutton(button_frame, text="Run Together", variable=self.run_mode_var, value="together")
        self.run_mode_radio_together.pack(side=tk.TOP, pady=2)
        self.run_mode_radio_together.config(state=tk.DISABLED)

        self.run_mode_radio_separate = tk.Radiobutton(button_frame, text="Run Separately", variable=self.run_mode_var, value="separate")
        self.run_mode_radio_separate.pack(side=tk.TOP, pady=2)
        self.run_mode_radio_separate.config(state=tk.DISABLED)

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

    def bind_tooltip_events(self, widget, text):
        # Bind tooltip show and hide events to a widget
        tooltip = ToolTip(widget, text)
        widget.bind("<Enter>", lambda event: tooltip.showtip())
        widget.bind("<Leave>", lambda event: tooltip.hidetip())

    def open_web(text):
        # Open a webpage (the help document) when the button is clicked
        webbrowser.open('https://docs.google.com/document/d/1yb6dg26jO_m0ir80vgfoN9ED0RF3bohMhJi0B3aig8w/edit?usp=sharing')

    def browse_file(self):
        # Browse for an input file and update the departments list based on the file's contents
        file_path = filedialog.askopenfilename()
        self.input_file_name.set(file_path)

        data_fields = get_data_dictionary()
        required_keys = [key for key, value in data_fields.items() if value['required']]
        with open(file_path, "r") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            if not all(key in csv_reader.fieldnames for key in required_keys):
                self.data_cleanup_wrapper()

        self.update_departments(self.input_file_name.get())

    def data_cleanup_wrapper(self):
        # Wrapper method to integrate the cleanup function in the GUI
        input_file = self.input_file_name.get()
        cleaned_file_path = data_cleanup(input_file)
        if cleaned_file_path:
            self.input_file_name.set(cleaned_file_path)

    def update_departments(self, file_path):
        # Update the list of departments based on the contents of the selected input file
        self.departments.clear()
        if not file_path:
            return

        with open(file_path, "r") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                if "Department" in row:
                    department = row["Department"]
                else:
                    # separate the department from the course code (CISC2512->CISC)
                    department = ''.join(filter(str.isalpha, row["CourseCode"]))

                if department not in self.departments:
                    self.departments.add(department)

        sorted_departments = sorted(self.departments)

        self.departments_listbox.delete(0, tk.END)
        for department in sorted_departments:
            self.departments_listbox.insert(tk.END, department)

    def update_radio_buttons_state(self, event=None):
        # Update the state of the run mode radio buttons based on the number of selected departments
        selected_departments = self.departments_listbox.curselection()
        if len(selected_departments) > 1:
            self.run_mode_radio_together.config(state=tk.NORMAL)
            self.run_mode_radio_separate.config(state=tk.NORMAL)
        else:
            self.run_mode_radio_together.config(state=tk.DISABLED)
            self.run_mode_radio_separate.config(state=tk.DISABLED)

    def select_all_departments(self):
        # Select or deselect all departments depending on the state of the select all checkbox
        if self.select_all_var.get():
            self.departments_listbox.select_set(0, tk.END)
        else:
            self.departments_listbox.selection_clear(0, tk.END)
        self.update_radio_buttons_state()

    def set_output_directory(self):
        # Set the output directory for the GSP results
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
                self.results = execute_tool(self.input_file_name.get(), min_supports, selected_departments, run_mode_var, self.output_directory)
            finally:
                self.progress.stop()
                self.progress.grid_forget()
                self.run_status_label.config(text="GSP finished running.\nVerify results in 'Output Directory'")

        # Run the GSP algorithm with the selected settings
        selected_departments = []
        for i in self.departments_listbox.curselection():
            selected_departments.append(self.departments_listbox.get(i))
        if not selected_departments:
            tk.messagebox.showwarning("No departments selected", "Please select at least one department to run GSP.")
        else:
            min_supports_str = self.min_supports_entry.get()
            min_supports = [int(s) for s in min_supports_str.split(",")]
            run_mode_var = self.run_mode_var.get()
            threading.Thread(target=target).start()

if __name__ == "__main__":
    root = tk.Tk()
    GSPTool(root)   # Run the GSP tool
