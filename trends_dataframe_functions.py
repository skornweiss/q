import pandas as pd
import re
from datetime import datetime
import openpyxl
import sys

# Define a regex pattern to match the 'Lastname, Firstname' format
name_pattern = r"^(?!.*?\b(?:last\s+name\s*,\s*first\s+name|last\s*,\s*first)\b)\s*[A-Za-z\- '\.]+(, Jr\.?|, Sr\.?|, I{1,3}|, IV|, V|, VI|, VII|, VIII|, IX|, X)?\s*,\s*[A-Za-z\- '\.]+\s*$"
   

def clean_trends_df(df):
    """Accepts a dataframe that comes from a raw lab trends excel file read by pandas read_csv
    and returns a pandas dataframe with the proper header row, with superfluous rows discarded,
    also removed columns with duplicate headers, drops columns with NaN headers,
    and replaces NaN data with blank strings"""

    # Find the header row (containing 'Ref range')
    ref_index = df[df.map(lambda x: x == 'Ref range')].any(axis=1).idxmax()
    
    # Set the columns based on the identified header row
    df.columns = df.iloc[ref_index]
    
    # Drop rows above and including the identified header row
    df = df[ref_index + 1:]
    
    # Reset index
    df.reset_index(drop=True, inplace=True)
    
    # Remove columns with duplicate headers
    df = df.loc[:, ~df.columns.duplicated(keep='first')]

    # Drop columns with header 'NaN'
    df = df.loc[:, ~df.columns.isna()]
    
    # Replace NaNs with blanks
    df = df.fillna("")

    # Truncate decimal values inside the DataFrame to one decimal point
    df = df.map(lambda x: '{:.2f}'.format(float(x)) if isinstance(x, (float, str)) and is_convertible_to_float(x) else x)
        
    return df

def validate_headers(df):
    """Accepts a pandas dataframe and removes any column that doesn't meet one of the following conditions:
    is in lastname, firstname format, is a valid date, or is the 'reference' column"""
    
    valid_columns = []
    
    for col in df.columns:
        col_str = str(col).strip()
        
        # Check if the column header matches the 'Lastname, Firstname' format
        if re.match(name_pattern, col_str, re.I):
            valid_columns.append(col)
        else:
            # Try interpreting the column as a date
            try:
                pd.to_datetime(col_str)
                valid_columns.append(col)
            except:
                pass

        # Check if the column header is the 'Reference' column
        if col_str == "Reference":
            valid_columns.append(col)
    
    # Keep only the valid columns
    df = df[valid_columns]
    return df

def format_date_headers(df):
    """Accepts a pandas dataframe, looks for headers that look like dates,
    and converts them to datetime in the format mm/dd/yy"""
    formatted_headers = []
    for header in df.columns:
        try:
            # Attempt to convert the header to a date and format it
            formatted_date = pd.to_datetime(header).strftime('%m/%d/%y')
            formatted_headers.append(formatted_date)
        except:
            # If it's not a date or can't be formatted, keep the original header
            formatted_headers.append(header)
    
    df.columns = formatted_headers
    return df

def sort_columns_reverse_chronological(df, reverse_chronological=True):
    """Accepts a pandas dataframe, differentiates date columns from non-date columns
    and then keeps the non-date columns in place while sorting the date columns in reverse-chronological order
    by default, or if indicated, in chronological order"""
    # Identify date columns and non-date columns
    date_cols = []
    non_date_cols = []
    for col in df.columns:
        try:
            pd.to_datetime(col)
            date_cols.append(col)
        except:
            non_date_cols.append(col)

    # Sort the date columns in reverse chronological order
    sorted_date_cols = sorted(date_cols, key=pd.to_datetime, reverse=reverse_chronological)
    
    # Concatenate the columns back together
    sorted_cols = non_date_cols + sorted_date_cols
    df = df[sorted_cols]
    
    return df

def is_convertible_to_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def id_category_rows(df):
    """Accepts pandas dataframe and adds a new column called 'category'
    that idenfies rows that are category rows as opposed to data rows"""
    # Identify category rows
    def is_blank_or_alpha(val):
        return pd.isna(val) or isinstance(val, str) and (val.strip() == '' or re.match(r'^[A-Za-z ]+$', val))

    df['is_category'] = df.apply(lambda row: all(is_blank_or_alpha(val) for val in row), axis=1)

    non_category_rows = df[df['is_category'] == False]
    
    return df

def is_date(string):
    try:
        datetime.strptime(string, '%m/%d/%y')
        return True
    except ValueError:
        return False
    
def identify_date_columns(df):
    date_columns = [col for col in df.columns if is_date(col)]
    return date_columns

def melt_dataframe(df):
    # Define the columns that should stay the same
    id_vars = ['test', 'category']

    # Melt the DataFrame
    melted_df = pd.melt(df, id_vars=id_vars, var_name='date', value_name='result')

    # Reorder the columns
    melted_df = melted_df[['test', 'result', 'date', 'category']]

    melted_df = melted_df.fillna('')


    return melted_df

def add_category_column(df,categories):
    current_category = None

    # Add a new 'category' column to the DataFrame
    df['category'] = ''

    for i, row in df.iterrows():
        # Check if the row is a category row
        if str(row['test']).lower() in categories:
            current_category = row['test']
        df.loc[i, 'category'] = current_category
    return df

def split_by_category(df, categories):
    print('TEST',df)
    dataframes = []
    current_df = pd.DataFrame(columns=df.columns)
    current_category = None

    for i, row in df.iterrows():
        # Check if the row is a category row
        # The 'test' column is one of the specified categories
        if str(row['test']).lower() in categories:
            # If we were already building a DataFrame, append it to the list
            if current_category is not None:
                dataframes.append((current_category, current_df))

            # Start a new DataFrame for the new category
            current_category = row['test']
            current_df = pd.DataFrame(columns=df.columns)
        else:
            # If the row is not a category row, append it to the current DataFrame
            current_df = pd.concat([current_df, pd.DataFrame(row).T])

    # Append the last DataFrame to the list, if it is not empty
    if not current_df.empty:
        dataframes.append((current_category, current_df))
    print(dataframes)
    return dataframes