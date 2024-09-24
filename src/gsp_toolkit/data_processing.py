from os import path, getcwd
import pandas as pd
from utils import get_data_dictionary

def data_cleanup(input_file_path):
    if not input_file_path:
        print("No input file selected. Please select an input file to run the tool on.")
        return None

    # Load the dataset
    df = pd.read_csv(input_file_path)

    # Dictionary to store the column mappings
    column_mapping = {}

    print("Please provide the corresponding column names in your dataset for each required field.")
    field_info = get_data_dictionary()
    
    # Loop over fields and prompt for user input
    for field, info in field_info.items():
        if info['required']:
            # Required fields: Must get valid input
            while True:
                user_input = input(f"Enter the column name for '{field}' (Required): ").strip()
                if user_input in df.columns:
                    column_mapping[field] = user_input
                    try:
                        df[user_input] = df[user_input].astype(info['dtype'])
                    except ValueError:
                        print(f"Error: Could not convert column '{user_input}' to {info['dtype']}. Please ensure the data is formatted correctly.")
                        continue
                    break
                else:
                    print(f"Error: Column '{user_input}' not found in the dataset. Please try again.")
        else:
            # Optional fields: Can skip
            user_input = input(f"Enter the column name for '{field}' (Optional, press Enter to skip): ").strip()
            if user_input:
                if user_input in df.columns:
                    column_mapping[field] = user_input
                    try:
                        df[user_input] = df[user_input].astype(info['dtype'])
                    except ValueError:
                        print(f"Warning: Could not convert column '{user_input}' to {info['dtype']}. Skipping this field.")
                else:
                    print(f"Warning: Column '{user_input}' not found in the dataset. Skipping this field.")
    
    # Edge case: If `Semester` and `Year` exist and the TermOrder has values less than 5 numbers, create new `TermOrder`
    if 'Semester' in df.columns and 'Year' in df.columns and df['TermOrder'].astype(str).str.len().max() < 5:
        def map_semester(semester):
            if semester.lower() == 'spring':
                return 0
            elif semester.lower() == 'summer':
                return 1
            elif semester.lower() == 'fall':
                return 2
            else:
                return None  # Handle unexpected values
        
        df['TermOrder'] = df.apply(lambda row: str(row['Year']) + str(map_semester(row['Semester'])), axis=1)
        # show the new TermOrder
        print("New TermOrder column has been created based on Year and Semester.")
        print(df['TermOrder'])
        df['TermOrder'] = df['TermOrder'].astype(int)
        
    # Keep only the columns that were successfully mapped
    df = df[list(column_mapping.values())]
    
    # Rename the columns to standard names 
    df = df.rename(columns={v: k for k, v in column_mapping.items()})

    # Apply Fordham-specific data cleanup
    df = df.drop(df[df['CourseCode'].isin([
        'CISC1610', 'CISC2010', 'CISC2110', 'PHYS1511', 'PHYS1512', 'PHYS2010', 'PHYS2011',
        'BISC1413', 'BISC1414', 'BISC2549', 'BISC2571', 'BISC3142', 'BISC3242', 'BISC3653',
        'BISC3231', 'BISC3415', 'CHEM1331', 'CHEM1332', 'CHEM2531', 'CHEM2532', 'CHEM2541',
        'CHEM2542', 'CHEM3631', 'CHEM3632', 'CHEM4231', 'CHEM4432'])].index)

    if 'FinalGrade' in df.columns:
        df = df.drop(df[df['FinalGrade'].isin(['W', 'INC', 'HPCE', 'PCE'])].index)

    # Save the cleaned data
    cleaned_file_path = path.join(getcwd(), f"cleaned_{path.basename(input_file_path)}")
    df.to_csv(cleaned_file_path, index=False)
    print("Data has been cleaned and saved to:", cleaned_file_path)

    return cleaned_file_path

def dataframe_gen(input_file_name, departments, run_mode, department_folder):
    """
    Generate a DataFrame from the input CSV file and filter based on departments and run mode.

    Args:
        input_file_name (str): The input CSV file name.
        departments (list): List of department codes to filter.
        run_mode (str): Run mode, either "separate" or "together."
        department_folder (str): Directory where department-specific files will be stored.

    Returns:
        dict or tuple: Results based on run mode, either a dictionary for separate departments or a tuple for all together.
    """
    def process_department_data(df, department_folder):
        """Process the data specific to a department, including sorting and resetting the index."""
        df = df.reset_index(drop=True)

        # assume TermOrder format is 'YYYYX' where X is the semester number
        df['Year'] = df['TermOrder'].astype(str).str[:-1].astype(int)  # Extract the year
        df['Semester'] = df['TermOrder'].astype(str).str[-1].astype(int)  # Extract the semester digit

        # sort by Year first, then Semester, and finally CourseCode
        sorted_df = df.sort_values(by=['Year', 'Semester', 'CourseCode'], ascending=[True, True, True])
        # Now, we can do operations like filtering by year or grouping by semester
        
        # Group by SID, collecting the CourseCode and TermOrder sequences
        sorted_df = sorted_df.groupby(['SID']).agg({
            'CourseCode': lambda x: list(x),
            'TermOrder': lambda x: list(x),
        }).reset_index()

        sorted_df = sorted_df.drop(columns=['SID'])

        # calculate transactions and insert delimiters
        transactions = len(sorted_df.index) + 1
        delimitor_df = insert_delimitor(sorted_df, department_folder)

        return transactions, sorted_df, delimitor_df

    df = pd.read_csv(input_file_name, low_memory=False)
    df = df.loc[df['CourseCode'].str[:4].isin(departments)]

    if run_mode == "separate":
        results = {}
        for department in departments:
            dfSub = df.loc[(df['Department'] == department)]
            results[department] = process_department_data(dfSub, department_folder)
        return results
    elif run_mode == "together":
        return process_department_data(df, department_folder)

def insert_delimitor(df, department_folder):
    """
    Insert delimiters between different semesters in the course code.

    Args:
        df (DataFrame): The DataFrame containing the course codes.
        department_folder (str): Directory where department-specific files will be stored.

    Returns:
        list: List of course codes with inserted delimiters.
    """
    course = [str(i).strip("[]").split(", ") for i in df.CourseCode]
    semester = [str(i).strip("[]").split(", ") for i in df.TermOrder]

    K_itemset = []
    updated_elem1 = []
    part1 = " "
    
    for i in range(len(semester)):
        start = 0
        elem1 = course[i]
        term1 = semester[i]
        item = term1[0]
        if len(term1) == 1:
            # only one course
            K_itemset.append(elem1[0])
        else:
            # all courses in same semester
            if len(set(term1)) == 1:
                part1 = ','.join(elem1)
                updated_elem1.append(part1)
            else:
                for j in range(0, len(term1)-1):
                    item1 = float(term1[j])
                    item2 = float(term1[j+1])
                    if item1 < item2:
                        part1 = ','.join(elem1[start:j+1])
                        start = j + 1
                        updated_elem1.append(part1)
                part1 = ','.join(elem1[start:len(elem1)])
                updated_elem1.append(part1)
                
            item = '|'.join(updated_elem1)
            K_itemset.append(item)
            updated_elem1.clear()
    
    d = {'CourseCode': K_itemset}
    new_df = pd.DataFrame(d)
    
    transactions_delimiter_file_path = path.join(department_folder, 'transactions_delimiter.csv')
    new_df.to_csv(transactions_delimiter_file_path)
    
    return(K_itemset) 