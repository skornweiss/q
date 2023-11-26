import pandas as pd
from dateutil.parser import parse
import re
from pathlib import Path
import os
import numpy as np
import re
import markdown as markdownmod
from datetime import datetime
import os

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False

def read_csv_with_mixed_header(filepath):
    # Open file and read lines until a line with both strings and dates is found
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            elements = line.split(',')
            if any(is_date(e) for e in elements) and any(not is_date(e) for e in elements):
                header_line = i
                break

    # Read CSV with the mixed line as header
    df = pd.read_csv(filepath, skiprows=header_line)
    
    # Remove blank columns
    df = df.dropna(how='all', axis=1)

    # Remove columns to the left of the column before the 'ref range' column
    ref_range_column_index = next((i for i, col in enumerate(df.columns) if re.match(r'ref(erence)?\s*range', col, re.I)), None)
    if ref_range_column_index is not None and ref_range_column_index > 0:
        df = df.iloc[:, ref_range_column_index - 1:]

    # Rename first two columns and make all 'test' values lowercase
    if len(df.columns) >= 2:
        df = df.rename(columns={df.columns[0]: 'test', df.columns[1]: 'range'})
        df['test'] = df['test'] #.str.lower()

    # Remove columns that don't have dates as headers (excluding 'test' and 'range')
    df = df.loc[:, [i for i in df.columns if i in ['test', 'range'] or is_date(i)]]

    # Remove leading and trailing whitespace around strings in the dataframe
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # Remove test names that also include units -- like lp(a) mg/dl
    df['test'] = df['test'].apply(replace_lpa)

    # Fix ApoE test name
    df['test'] = df['test'].apply(replace_apoe)

    # Fix egfr field
    df['test'] = df['test'].apply(replace_egfr)

    # Fix prostate velocity field
    df['test'] = df['test'].apply(replace_psa_velocity)

    # Make the whole damn dataframe lowercase
    #df = df.applymap(lambda s: s.lower() if type(s) == str else s)



    return df

def replace_lpa(s):
    if isinstance(s, str):
        if re.search(r'lp\(a\)', s, re.IGNORECASE):
            return 'Lp(a)'
    return s

def replace_apoe(s):
    if isinstance(s, str):
        if re.search(r'apoe', s, re.IGNORECASE):
            return 'ApoE'
    return s

def replace_egfr(s):
    if isinstance(s, str):
        if re.search(r'egfr', s, re.IGNORECASE):
            return 'egfr'
    return s

def re_replace_egfrs_with_cystatincegfr(s):
    if isinstance(s,str):
        if re.search(r'egfr',s,re.IGNORECASE):
            return 'eGFR by Cystatin-C'
    return s

def replace_psa_velocity(s):
    if isinstance(s,str):
        if re.search(r'psa velocity',s,re.IGNORECASE):
            return 'psa velocity'
    return s
    
def dump_test_and_range(df, filename):
    # Select 'test' and 'range' columns
    selected_df = df[['test', 'range']]

    # Drop duplicates
    selected_df = selected_df.drop_duplicates()

    # Write to CSV
    selected_df.to_csv(filename, index=False)


def split_by_category(df):
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

    return dataframes


def add_category_column(df):
    current_category = None

    # Add a new 'category' column to the DataFrame
    df['category'] = ''

    for i, row in df.iterrows():
        # Check if the row is a category row
        if str(row['test']).lower() in categories:
            current_category = row['test']
        df.loc[i, 'category'] = current_category
    return df

def melt_dataframe(df):
    # Define the columns that should stay the same
    id_vars = ['test', 'category']

    # Melt the DataFrame
    melted_df = pd.melt(df, id_vars=id_vars, var_name='date', value_name='result')

    # Reorder the columns
    melted_df = melted_df[['test', 'result', 'date', 'category']]

    melted_df = melted_df.fillna('')


    return melted_df

def check_range(result, range_str):
    # If result is a string containing %, skip the row
    if isinstance(result, str) and '%' in result:
        return None
    
    # Try to convert result to float, if not possible, skip the row
    try:
        result_float = float(result)
    except ValueError:  # If conversion is not possible, return None and skip the row
        return None
    
    # Ensure range_str is a string for the following checks
    range_str = str(range_str)

    # Handling range specifications
    if range_str.startswith('<'):
        try:
            upper_limit = float(range_str[1:])
        except:
            return None
        if result_float >= upper_limit:
            return 'H'
    elif range_str.startswith('>'):
        try:
            lower_limit = float(range_str[1:])
            if result_float <= lower_limit:
                return 'L'
        except:
            return None
    elif '-' in range_str:
        lower_limit, upper_limit = map(float, range_str.split('-'))
        if result_float < lower_limit:
            return 'L'
        elif result_float > upper_limit:
            return 'H'
    
    return None  # If result is within range or range format is unrecognized


def categorize_single_result_tests(df, test_names):
    
    # Iterate over test names
    for test in test_names:
        # Create mask for rows where 'test' column contains the test name
        mask = df['test'].str.contains(test, case=False, na=False)

        # Assign 'single-tests' category to matching rows
        df.loc[mask, 'category'] = 'genetics'

    return df

def recategorize(row, category_dict):
    # Lookup the test name in the category_dict, return the original category if not found
    return category_dict.get(row['merge_key'], row['category'])

# Define your dictionary here. This should include all test-category pairs.
category_dict = {
    'psa': 'prostate',
    'hb': 'hematology',
    'ferritin': 'hematology',
    'iron':'hematology',
    'egfr - cystatin c': 'renal',
    'egfr':'renal',
    'cystatin c':'renal',
    'urinalysis':'renal',
    'tsh':'thyroid',
    'ft4':'thyroid',
    'ft3':'thyroid',
    'homocysteine':'metabolic',
    'hscrp':'metabolic',
    'uric acid':'metabolic',
    'homocysteine':'metabolic',
    'vitamin b12':'vitamins',
    'vitamin d':'vitamins',
    'folate':'vitamins',
    'mthfr':'genetics',
    'egfr by cystatin-c':'renal',
    'eGFR by Cystatin-C':'renal',
    'omega-3':'fatty acids',
    'psa velocity':'prostate',
    'lp(a)':'lipoproteins',
    # Add more tests and their new categories as necessary.
}

pattern = r'\|(-+\|)+'
def format_table(match):
    groups = match.group().split('|')[1:-1]
    first, *middle, last = groups
    return '|:' + '-'*len(first) + ':|' + ''.join([':' + '-'*len(m) + ':|' for m in middle]) + ':' + '-'*len(last) + ':|'

sex_hormone_order = ['estradiol','fsh','lh','shbg','testosterone','free testosterone']
sterol_order = ['campesterol','sitosterol','lathosterol','desmosterol']
lipid_order = ['ldl-c','hdl-c','triglycerides','non-hdl-c','vldl-c','tg/hdl-c']
metabolic_order = ['homocysteine','hscrp','uric acid','insulin','hba1c','estimated average glucose','fasting glucose']
thyroid_order = ['tsh','ft4','ft3']
hematology_order = ['hb','iron','ferritin']
liver_order = ['alt','ast']

def sort_dataframe_by_list(df, column, order_list):
    # Create a mapping dictionary from the order list, ignoring case
    order_dict = {item.lower(): item for item in order_list}
    
    # Create a new column with values from the specified column, but transformed to match the order list
    df['temp_sorting_column'] = df[column].apply(lambda x: order_dict.get(str(x).lower(), x) if isinstance(x, str) else x)
    
    # Convert the new column to a categorical type with the order specified by the order list
    df['temp_sorting_column'] = pd.Categorical(df['temp_sorting_column'], categories=order_list, ordered=True)
    
    # Sort the dataframe by the new column
    df_sorted = df.sort_values(by='temp_sorting_column')
    
    # Drop the temporary sorting column
    df_sorted = df_sorted.drop('temp_sorting_column', axis=1)
    
    return df_sorted

def dump_to_markdown(df, filename,ranges):
    with open(filename, 'w') as f:
        for category in categories:
            
            # Filter the DataFrame by the category
            category_df = df[df['category'].str.lower() == category.lower()]

            # Bold any results that are flagged H or L in flag column
            #category_df['result'] = category_df.apply(lambda row: f"=={row['result']}==" if row['flag'] in ['H', 'L'] else row['result'], axis=1)

            # Unmelt the DataFrame
            category_df = category_df.pivot_table(index=['test'], columns='date', values='result', aggfunc='first').reset_index()

            # Sort dataframe using custom order
            if category == 'sex hormones':
                category_df = sort_dataframe_by_list(category_df,'test',sex_hormone_order)

            if category == 'sterols':
                category_df = sort_dataframe_by_list(category_df,'test',sterol_order)

            if category == 'lipids':
                category_df = sort_dataframe_by_list(category_df,'test',lipid_order)

            if category == 'metabolic':
                category_df = sort_dataframe_by_list(category_df,'test',metabolic_order)

            if category == 'thyroid':
                category_df = sort_dataframe_by_list(category_df,'test',thyroid_order)

            if category == 'hematology':
                category_df = sort_dataframe_by_list(category_df,'test',hematology_order)

            if category == 'liver':
                category_df = sort_dataframe_by_list(category_df,'test',liver_order)

            # Capitalize column headers
            category_df.columns = [col.title() for col in category_df.columns]

            # Sort date columns
            non_date_columns = ['Test']
            date_columns = [col for col in category_df.columns if col not in non_date_columns]
            date_columns.sort(key=pd.to_datetime, reverse=True)  # Convert to datetime and sort
            
            
            #date_columns = date_columns[:3]
            category_df = category_df[non_date_columns + date_columns]  # Reorder columns

            ranges = pd.read_csv(ideal_lab_ranges_file)
            category_df['merge_key'] = category_df['Test'].str.lower()

            category_df = category_df.merge(ranges, left_on='merge_key', right_on='test', how='inner')
            category_df['Test'] = category_df['Test'].apply(re_replace_egfrs_with_cystatincegfr)
            if category_df.empty:                
                continue

            # Dump na values
            category_df = category_df.fillna('')
            category_df = category_df.rename(columns={'range_male':'Reference'})
            print(category_df.columns)
            category_df['Test'] = category_df.apply(lambda row: f"{row['Test']} <span class='unit'>({row['units']})</span>" if row['units'] else row['Test'], axis=1)
            category_df = category_df.drop(columns=['test','range_female','units','merge_key'])
            # get rid of ranges entirely
            #category_df = category_df.drop(columns=['Range'])

            for col in date_columns:
                new_col_name = datetime.strptime(col, "%Y-%m-%d %H:%M:%S").strftime('%m/%d/%Y')
                print(new_col_name)
                category_df.rename(columns={col: new_col_name}, inplace=True)
            
            print(category_df)
            
            
            category_df = category_df.rename(columns={'Test':''})
            print(category_df.columns)

            # Capitalize the test names
            #category_df['Test'] = category_df['Test'].str.title()

            # select certain columns to write to markdown
            # Write the DataFrame as a markdown table
            markdown = category_df.to_markdown(index=False, tablefmt='github')
            
            # reformat markdown table - left justify left col, middle all others, right right
            formatted_markdown = re.sub(pattern, format_table, markdown)
            html = markdownmod.markdown(formatted_markdown, extensions=['tables'])
            print(html)
            
            
            f.write(f'#### {category.title()}\n\n\n')  # Write the category name as a header
            f.write(markdown)
            f.write('\n\n+++\n\n')  # Add some space between categories
            #concatdf = pd.DataFrame()
            #concatdf.concat(category_df)

prep_template_file_path = "/Volumes/asha_crep/templates/lab_prep_email_old_template.md"
def write_lab_prep_doc(df,prep_template_file_path,output_dir,suffix):
    dfc = df.copy()
    # Equivalent test names mapping
    equivalent_tests = {
        'hba1c': ['hga1c', 'hba1c', 'a1c'],
        'hgb': ['hgb', 'hemoglobin', 'hb'],
        'vitamin d':['vitd','vitamin d'],
        'tbili':['tbili','total bilirubin'],
        'e2': ['e2','estradiol'],
        'free t': ['free t', 'free testosterone'],
        'testosterone': ['testosterone','total testosterone', 'total t'],
        'psa':['PSA','psa'],
        'hscrp':['hscrp','hs-crp']
    }

    def expand_equivalents(mapping):
        expanded = {}
        
        for key, values in mapping.items():
            for value in values:
                expanded[value] = values
        return expanded

    expanded_equivalents = expand_equivalents(equivalent_tests)
    
    def replacer(match):
        return match.group(0) + ' ' + str(recent_value) # ) + str(f' ({recent_date})')

    dfc['test'] = dfc['test'].str.lower()
    dfc['date'] = pd.to_datetime(dfc['date'], format='mixed', errors='coerce')


    with open(prep_template_file_path,'r') as file:
        document= file.read()
    # Extract the header from the document
    import re
    header_pattern = re.compile(r'^---(.*?)(?![|:])---', re.DOTALL)

    match = header_pattern.search(document)
    if match:
        header = match.group(1)
        # Loop through unique test names
        for test in dfc['test'].unique():
            # Get the most recent value for that test
            most_recent_row = dfc[dfc['test'] == test].sort_values(by='date', ascending=False).iloc[0]
            recent_value = most_recent_row['result']
            recent_date = most_recent_row['date'].strftime("%Y%m%d")
            todays_date = datetime.now().strftime("%Y%m%d")
            if 'a1c' in test:
                print(type(recent_value))
                eag = int((float(recent_value)*28.7) - 46.7)
                header += f'eag:{eag}\n'
            
            # If the test has equivalent names, loop through each one
            for equivalent_test in expanded_equivalents.get(test, [test]):
                # Create a pattern that matches test names, treating spaces and underscores as equivalent
                pattern_string = equivalent_test.replace(' ', '[ _]')
                pattern = re.compile(f'{pattern_string}:', re.IGNORECASE)
                # Replace in the header using re.sub
                if pattern.search(header):
                    header = re.sub(pattern, replacer, header)
        
        # Replace the original header with the modified header in the document
        document = re.sub(header_pattern, f'---{header}---', document)
    file.close()
    output = os.path.join(output_dir,f'{recent_date}_{suffix}.md')
    with open(output, 'w') as file:
        file.write(document)

def main(filename):
    filename = convert_xlsx_to_csv(filename)
    ptname = os.path.basename(filename).split('_',1)[0].replace(', ','_')
    print(ptname)
    outputdir = Path(filename).parent
    output_file = os.path.join(outputdir, f'{ptname}_lab_trends')
    final_dir = os.path.basename(outputdir)
    markdown_file = f"{output_file}.md"
    csv_file = f"{output_file}.csv"

    orig_df = read_csv_with_mixed_header(filename)

    ideal_lab_ranges_file = '/Volumes/asha_crep/programming/ideal_lab_ranges_labcorp.csv'
    #dump_test_and_range(orig_df,test_and_range_csv)

    df = add_category_column(orig_df)
    
    # Remove the range column
    df.drop([col for col in df.columns if 'range'.lower() in col.lower()], axis=1, inplace=True)
    df = df[~df['test'].str.lower().isin(categories)]
    df = df.fillna('')

    global melted_df
    melted_df = melt_dataframe(df)
    
    
    melted_df['category'] = melted_df['category'].replace({'Other':'additional biomarkers'})

    write_lab_prep_doc(melted_df,prep_template_file_path,outputdir,'prep_email_draft')
    patient_note_template_path='/Volumes/asha_crep/templates/patient_note_template_2.md'
    write_lab_prep_doc(melted_df,patient_note_template_path,outputdir,'patient_note_draft')

    df2 = categorize_single_result_tests(melted_df, ['lp\(a\)','apoe'])
    df3 = df2.replace(r'^\s*$', np.nan, regex=True).dropna(how='any')
    ranges = pd.read_csv(ideal_lab_ranges_file)
    df3['merge_key'] = df3['test'].str.lower()

    global merged
    merged = df3.merge(ranges, left_on='merge_key', right_on='test', how='outer')
    #merged = df3.drop(columns=['merge_key'])

    # Recategorize based on the above dictionary (i.e. put psa into the prostate category)
    merged['category'] = merged.apply(lambda row: recategorize(row, category_dict), axis=1)

    merged = merged.rename(columns={'test_x':'test'})

    # Add a flag column and check ranges
    merged['flag'] = merged.apply(lambda row: check_range(row['result'], row['range_male']), axis=1)
    
    def round_floats(value):
        # Check if value is already a float
        if isinstance(value, float):
            return round(value, 1)
        # Try to convert string to float and round it
        try:
            return round(float(value), 1)
        except (ValueError, TypeError):
            return value  # Return original value if not convertible to float

    # Apply the function to each element of the DataFrame
    merged = merged.applymap(round_floats)



    dump_to_markdown(merged,markdown_file,ranges)
    
    global fmerged
    fmerged = merged[selected]
    fmerged['test'] = fmerged['test'].apply(re_replace_egfrs_with_cystatincegfr)
    print(csv_file)
    fmerged.to_csv(csv_file,index=False)
    
    '''
    f = open(os.path.join(outputdir,'lab_trends.md'),'w')
    f.write(markdown)
    f.close()
    '''
    return(csv_file, melted_df)

def convert_xlsx_to_csv(path):
    # Use pandas to read the Excel file and save as CSV
    df = pd.read_excel(path)
    # Round float columns to two decimal places
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].round(2)

    # Keep only the date part of datetime columns
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            df[col] = df[col].dt.date
    csv_filename = path.name.replace('.xlsx', '.csv')
    df.to_csv(csv_filename, index=False)

    return csv_filename

def list_lab_trends_files(path):
    # List all files in the specified directory
    files = os.listdir(path)

    # Filter for .xlsx files that contain "lab trends" (case insensitive)
    lab_trends_files = [os.path.join(path, f) for f in files if f.lower().endswith('.xlsx') and 'lab trends' in f.lower()]

    return lab_trends_files

ideal_lab_ranges_file = '/Volumes/asha_crep/programming/ideal_lab_ranges_labcorp.csv'
categories = ['lipoproteins','lipids', 'sterols', 'genetics','metabolic markers',
              'inflammatory markers', 'metabolic','vitamins','renal','thyroid',
              'sex hormones','prostate','liver','hematology',
              'fatty acids','additional biomarkers','other']
selected = ['date','test','result','units','range_male','category','flag']


#if __name__ == "__main__":
    #xl_filenames = list_lab_trends_files(path)
    #while xl_filenames:
    #filename = convert_xlsx_to_csv(xl_filenames.pop())
    #print(filename)
    #main(filename)