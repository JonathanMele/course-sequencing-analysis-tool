from os import path, getcwd
import pandas as pd
from utils import get_data_dictionary

def data_cleanup(input_file_path):
    return

def dataframe_gen(df, departments, run_mode, department_folder):
    """
    Generate a DataFrame from the input CSV file and filter based on departments and run mode.
z
    Args:
        df (DataFrame): The input DataFrame.
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
        
        # Group by ID, collecting the CourseCode and TermOrder sequences
        sorted_df = sorted_df.groupby(['ID']).agg({
            'CourseCode': lambda x: list(x),
            'TermOrder': lambda x: list(x),
        }).reset_index()

        sorted_df = sorted_df.drop(columns=['ID'])

        # calculate transactions and insert delimiters
        transactions = len(sorted_df.index) + 1
        delimitor_df = insert_delimitor(sorted_df, department_folder)

        return transactions, sorted_df, delimitor_df

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