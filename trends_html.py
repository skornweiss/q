
    
def html_date_headers_with_hover_tooltip(df):
    # Identify date columns based on a stricter pattern check
    date_columns = identify_date_columns(df)
    
    for i in range(len(date_columns)):
        dt_obj = datetime.strptime(date_columns[i], '%m/%d/%y')
                
        # If there's a next date (i.e. previous in chronological order)
        if i+1 < len(date_columns):
            next_dt_obj = datetime.strptime(date_columns[i+1], '%m/%d/%y')
            elapsed_weeks = (dt_obj - next_dt_obj).days // 7
            elapsed_str = f"{elapsed_weeks} weeks elapsed"
        else:
            elapsed_str = "Initial Draw"
        date_tip_str = f"<div class='date_tip'>%A<br>%m.%d.%y<br>{elapsed_str}</div>"
        date_str = "%b<br><span class='year'>%Y</span>"
        new_col_name = dt_obj.strftime(f"<div class='header-content'>{date_str}{date_tip_str}</div>")
        df.rename(columns={date_columns[i]: new_col_name}, inplace=True)

    return df

def to_markdown(df):
    return df.to_markdown(index=False)

def to_html(df):
        # Base styles
    styles = {
        "font-family": "Avenir LT Std 55 Roman",
        "border": "1px solid #e0e0e0",
        "border-collapse": "collapse",
        "text-align": "left",
        "padding": "10px 15px"
    }

    # Convert dictionary of styles to a single string
    style_str = "; ".join([f"{key}: {value}" for key, value in styles.items()])

    # Hover effects for cells
    hover_effect = {
        "selector": "tbody tr:hover td, tbody tr:hover th",
        "props": [("background-color", "rgba(218, 89, 85, 0.5)")]
    }

    alternate_row_color = {
        "selector": "tbody tr:nth-child(even)",
        "props": [("background-color", "#f7f7f7")]
    }

    no_wrap_style = {
        "selector": "td, th",
        "props": [("white-space", "nowrap")]
    }

    table_auto_layout = {
        "selector": "table",
        "props": [("table-layout", "auto")]
    }

    # Create the Styler object
    styled = df.style.set_table_attributes(f'style="{style_str}"').set_properties(**styles)

    # Header style (sticky)
    header_style = {
        "selector": "thead th",
        "props": [
            ("font-family", "Avenir"),
            ("background-color", "#f2f2f2"),
            ("border-bottom", "2px solid #000"),
            ("font-size", "1em"),  # Increase font size
            ("position", "sticky"),
            ("top", "0"),  # Stick to the top
            ("z-index", "1"),  # Ensure header is on top of content
        ]
    }

    # Apply all styles
    all_styles = [header_style, hover_effect, alternate_row_color, no_wrap_style, table_auto_layout]
    styled = styled.set_table_styles(all_styles)

    # Convert the DataFrame to HTML
    table_html = styled.to_html(index=False)

    # Wrap the first column in a separate div for sticky effect
    first_col_sticky = f'<div class="sticky-first-col">{table_html}</div>'

    # Apply CSS to make the first column sticky
    style = '''
        <style>
            .sticky-first-col {
                overflow-x: auto;
            }
            .sticky-first-col table {
                table-layout: fixed;
            }
            .sticky-first-col td:first-child, .sticky-first-col th:first-child {
                position: sticky;
                left: 0;
                background-color: #fff;
            }
        </style>
    '''

    # Combine the style and table HTML
    full_html = f'{style}{first_col_sticky}'

    return full_html

def save_to_files(df, md_file, html_file):
    with open(md_file, 'w') as file:
        file.write(to_markdown(df))
    
    # Convert to HTML with category row classes
    html_content = to_html(df)
    lines = html_content.split('\n')
    modified_lines = []
    row_index = 0  # Initialize the row index
    for line in lines:
        if '<tr>' in line:
            if row_index < df.shape[0]:  # Check if the row index is within bounds
                if df.iloc[row_index, -1]:
                    line = line.replace('<tr>', '<tr class="category-row">')
                row_index += 1  # Increment the row index
        modified_lines.append(line)
    
    modified_html_content = '\n'.join(modified_lines)

    with open(html_file, 'w') as file:
        file.write(modified_html_content)

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
    
    # Attempt to convert the column headers to dates and store them in a list
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
    html += "</tr></thead><tbody>"

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

def save_html_to_file(df, html_file):
    html_content = generate_html(df)
    
    with open(html_file, 'w') as file:
        file.write(html_content)


def open_file():
    filepath = filedialog.askopenfilename(title="Open Excel File",
                                          filetypes=[("Excel Files", "*.xls;*.xlsx"),
                                                     ("All Files", "*.*")])
    print(filepath)

def processed_df(input_file):
    df = read_and_clean_excel(input_file)
    df = validate_data(df)
    df = format_date_headers(df)
    df = apply_formatting(df)
    df = sort_columns_reverse_chronological(df)
    #df = spell_out_date_headers(df)
    return df

def main(path):
  
    input_file=path
    # Example usage:
    df = read_and_clean_excel(input_file)
    df = validate_data(df)
    df = format_date_headers(df)
    df = apply_formatting(df)
    df = sort_columns_reverse_chronological(df)
    df = spell_out_date_headers(df)
    html_content = generate_html(df)

    
    save_to_files(df, "output.md", "output.html")
    save_html_to_file(df, "output2.html")