import pandas as pd
import re
from datetime import datetime
import openpyxl
import sys

import plotly.express as px
import plotly.graph_objects as go
import numpy as np


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
    #df = df.map(lambda x: '{:.2f}'.format(float(x)) if isinstance(x, (float, str)) and is_convertible_to_float(x) else x)
        
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


def create_plotly_line_plot_of_metric(dataframe, metric_name):
    df = dataframe
    df = df.query(f'test.str.lower() == @metric_name').replace('',np.nan).dropna()
    if df.empty:
        return
    df.sort_values(by='date',inplace=True)
    fig = px.line(df, x='date', y='result', title=f'{metric_name}'.upper())
    fig.update_xaxes(tickmode='array',tickvals=df['date'],tickformat="%m/%d/%y")
    for x, y in zip(df['date'], df['result']):
        fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers', marker=dict(color='black', size=6), showlegend=False))
        fig.add_annotation(x=x, y=y, text=str(y), showarrow=False, yshift=12, xshift=5, font=dict(color="black"))
    return fig

def generate_html(df):
    
    # Start the HTML with the base structure and styles
    html = """
    <html>
    <head>
        <style>
            /* Base styles */
            table {
                font-family: "Avenir";
                border: 1px solid rbg(5,5,5);
                border-collapse: collapse;
                /*table-layout: auto;
                width: auto;*/
                margin: 0 auto;
                font-size:1.2em;
            }

            th, td {
                text-align: left;
                white-space: nowrap;
                padding: 12px;
                min-width: 60px;
            }

            th {
                font-family: "cormorant garamond";
                background: radial-gradient(circle, #1a212a, #06121b);
                background-color: grey;
                border: none;
                border-bottom: 1px solid grey;
                box-shadow: -1px 0 0 2 #000,  /* left border */
                 1px 0 0 2 #000;  /* right border */
                font-size: 1.1em;
                text-align: center !important;
                position: sticky;
                top: -1px;
                z-index: 10;
                height: 100px;
                color: eceeee;
                padding: 3px;
            }

            th {
                box-shadow: 0px 0px 1px #000, /* right border */
                            -1px 0 0px #000;  /* left border */
                z-index:10;
            }

            /**, *:before, *:after {
                box-sizing: border-box;
            }*/


            td {
                white-space: nowrap;
                border: 1px solid rgb(200,200,200);
            }

            td:nth-child(2), th:nth-child(2) {
                padding:10px;
                width:100px;
            }

            /* Styles for the sticky first column */
            th:first-child, td:first-child {
                position: sticky;
                left: -1px;
                z-index: 1;
                //background-color: white; /* This should be a default color for the sticky first column */
                font-weight: bold;
            }

            th:first-child {
                z-index: 4;
                top: -1px;
                left: -1px;
                //background-color: grey;
            }

            /* Hover effects only for non-category rows */
            tbody tr:not(.category-row):hover td,
            tbody tr:not(.category-row):hover th {
                background-color: #82b3fd;
                transition: background-color 0.3s ease-in-out; /* Add a smooth transition effect */
                color: white;
                font-weight:bold;
            }

            /* Category row styles */
            tr.category-row td:not(:first-child) {
                //font-size: 0;
                //color:white;
            }
            tr.category-row, 
            tr.category-row td, 
            tr.category-row th {
                //background-color: #267dff;
                border: none;
                font-family: "cormorant garamond";
                font-weight:strong;
                font-size:20px;
                text-transform: uppercase;
                color:#ECEEEE;
                text-align:center;
            }
            tr.category-row td:first-child, 
            tr.category-row th:first-child {
                //background-color: #267dff;
                text-align:left;
            }


            .sticky-first-col table {
                table-layout: fixed;
            }
            .sticky-first-col th:first-child, 
            .sticky-first-col td:first-child {
                //background-color: #fff;
            }

            

            /* Right-align content for column 3 and higher */
            td:nth-child(n+3) {
                text-align: right;
            }

            td:nth-child(n+3) {
                max-width: 50px;
            }            

            /* Set an opaque background for the header of the most recent date column */
            th[data-latest="true"] {
                background-color: rgb(130, 179, 253);
                z-index: 9999;  /* To ensure the header stays above other cells */
            }


            /* Alternate row color for even rows */
            tr:nth-child(even) {
                background-color: #E2E4E4;
                z-index:1;
            }

            td.highlight {
                background-color: rgba(130, 179, 253, 0.5); /* Highlight color */
                transition: background-color 0.3s ease-in-out; /* Add a smooth transition effect */
                font-weight:600;
                border:none;
            }

            

            .header-content:not(.date-tip) {
                //transform: rotate(-90deg);
                white-space: nowrap;
            }

            .date_tip {
                position: absolute;
                font-family: 'avenir';
                font-size: 0.85em;
                transform: translateX(-50%);  /* To ensure perfect centering */
                background-color: rgb(0,0,0,0.99);
                color: white;
                border-radius: 8px;
                border: none;
                padding: 20px;
                z-index: 20;
                margin-top: 5px;  // to position it just below the date.
                white-space: nowrap; // to prevent wrapping inside the tooltip.
                opacity: 0;  /* Initially transparent */
                visibility: hidden;
                transition: opacity 0.9;  /* Delayed fade in */
            }

            .year {
                font-size: 1.3em;
            }

            /* Tooltip styling on TH cell hover */
            th:hover .date_tip {
                opacity: 0.9;  /* Fully opaque */
                visibility: visible;
                top: 100%;
                left: 50%;
            }

            /* Apply reverse rotation to un-rotate the tooltip within the rotated header
            .header-content:not(.date-tip) .date_tip {
                transform: rotate(90deg);
                transform-origin: top right;
            }

            .header-content {
                position: relative; // makes sure the absolute positioning of the tooltip is in relation to this container.
            }*/

            /* Style for the most recent date column */
            td[data-latest="true"], th[data-latest="true"] {
                background-color: rgba(130, 179, 253);
            }

            .folded {
                /*display: none;*/
            }

             /* Style for odd rows */
            tr:nth-child(odd) td:first-child {
               background-color: white;
            }
            
            /* Ensure the first column of even rows gets the alternate color */
            tr:nth-child(even) td:first-child {
                background-color: #E2E4E4;
            }

            tr.category-row {
                position:relative;
                background-color: none;
                background-opacity: 0;
                background: linear-gradient(to right, #267dff, #da5955); /* Adjust colors as desired */
                
            }

            tr.category-row > td:first-child {
                background-color: rgb(0,0,0,0);
            }

           

        </style>


 
    </head>
    <body>
    <div>
    
        <table>
    """
    
    """# Attempt to convert the column headers to dates and store them in a list
    date_cols = []
    for col in df.columns:
        try:
            date_obj = pd.to_datetime(col)
            date_cols.append(date_obj)
        except:
            # If conversion fails, it's not a date string
            pass

    # Find the most recent date
    most_recent_date = max(date_cols) if date_cols else None

    if most_recent_date:
        most_recent_date = most_recent_date.strftime('%m/%d/%y')
    else:
        most_recent_date = None

    print(most_recent_date)

    # The rest of the code remains the same


    # Start generating the HTML table with headers
    html += "<table><thead><tr>"

    # Generate headers
    for col in df.columns:
        if col != 'is_category':
            if col == most_recent_date:
                html += f'<th data-latest="true">{col}</th>'
            else:
                html += f'<th><span>{col}</span></th>'
    html += "</tr></thead><tbody>"""

    for col in df.columns:
        html += f'<th><span>{col}</span></th>'

    # Loop through rows to generate table data
    for _, row in df.iterrows():
        if row["is_category"]:
            html += '<tr class="category-row">'
        else:
            html += "<tr>"
        for col in df.columns:
            if col != 'is_category':  # Exclude the 'is_category' column
                if col == most_recent_date:
                    html += f'<td data-latest="true">{row[col]}</td>'
                else:
                    html += f'<td>{row[col]}</td>'
        html += "</tr>"


    
    # Close the HTML tags
    html += """
        </tbody>
        
        </table>
        <!-- Add a hidden div for displaying the graph -->
        <div id="graphPopup" style="display: none;"></div>
       <script>
            // Get all header cells
            const headerCells = document.querySelectorAll('th');

            // Array to store indices of highlighted columns
            const highlightedColumns = [];

            // Add click event listeners to header cells
            headerCells.forEach((headerCell, index) => {
            headerCell.addEventListener('click', () => {
                // Check if the column is already highlighted
                const isHighlighted = highlightedColumns.includes(index);

                // Toggle highlight status
                if (isHighlighted) {
                // Remove highlight from the column
                headerCell.classList.remove('highlight');
                const cellsInColumn = document.querySelectorAll(`td:nth-child(${index + 1})`);
                cellsInColumn.forEach(cell => cell.classList.remove('highlight'));

                // Remove index from the array
                const indexToRemove = highlightedColumns.indexOf(index);
                highlightedColumns.splice(indexToRemove, 1);
                } else {
                // Add highlight to the column
                headerCell.classList.add('highlight');
                const cellsInColumn = document.querySelectorAll(`td:nth-child(${index + 1})`);
                cellsInColumn.forEach(cell => cell.classList.add('highlight'));

                // Add index to the array
                highlightedColumns.push(index);
                }
            });
            });
            // Get all table rows
            const rows = document.querySelectorAll('tbody tr');

            // Add contextmenu event listener to each row
            rows.forEach(row => {
                row.addEventListener('contextmenu', event => {
                    event.preventDefault(); // Prevent the default context menu
                    event.stopPropagation();

            // Move the row to the hidden rows container
            hiddenRowsContainer.appendChild(row);

            // Remove the "folded" class to ensure it's visible
            row.classList.remove('folded');
        });
        });

        // Add click event listener to the category row to toggle collapsible content
        const categoryRow = hiddenRowsContainer.querySelector('.category-row');
        categoryRow.addEventListener('click', () => {
        // Toggle the "folded" class on the next elements (hidden rows)
        const collapsibleRows = document.querySelectorAll('#hiddenRowsContainer tr:not(.category-row)');
        collapsibleRows.forEach(row => {
            row.classList.toggle('folded');
            
            });
        });


            
            
            </script>
    </body>
    </html>
    """
    
    return html

def zebra_striping(s):
    return ['background-color: #ebebeb' if i % 2 else '' for i in range(len(s))]
