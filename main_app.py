import streamlit as st
import pandas as pd
from io import StringIO
from dateutil.parser import parse

import trends_dataframe_functions as tdf
from datetime import date
from trends_constants import *

st.echo(categories)

# App Title
st.title("Test")

# Dash
#st.metric("Date", date.ctime(date.today()))

# Sidebar
# Add file-uploader to sidebar
file = st.sidebar.file_uploader('Select File', help="Select an excel lab trends sheet")

a = pd.DataFrame()
#a.style.format(precision=2,hidd)


if file is not None:
    
    df = pd.read_excel(file, parse_dates=True, header=None, index_col=None)
    df = tdf.clean_trends_df(df)
    df = tdf.validate_headers(df)
    df = tdf.format_date_headers(df)
    
    # Adds 'is_category' column set to True for rows that are category rows
    df = tdf.id_category_rows(df)
        
    # Example of how to style float precision for display
    #styled_df = df.style.format(precision=2)
    #styled_df

    # Identifies category rows and puts them into a list for styling
    #cat_rows = df.index[df['is_category'] == True].tolist()
    #styled_df = styled_df.set_properties(subset=pd.IndexSlice[cat_rows,:],**{'background-color':'black','color':'white'})
    #styled_df

    # Get  name in case we want it, but then immediately over-write if not using
    patient_name = df.columns[0]
    patient_name = '4;tqoiheg;iheg;43htq34d;lkj'
    del(patient_name)
    df.rename(columns={df.columns[0]:'test'},inplace=True)

    df_melted = pd.melt(df,id_vars=[df.columns[0]],value_name="result",var_name="date")
    df_melted = tdf.add_category_column(df_melted,categories)
    df_melted = df_melted.query('date !="is_category"')
    df_melted["date"] = pd.to_datetime(df_melted["date"])
        
    # Test names to make plots for
    tests_to_plot = ['apob','free testosterone','psa']

    # Make tables to display the dataframe for each category of test separately
    for cat in categories:
    
        # Query the larger dataframe for tests that fall into a specific category
        query = 'category.str.lower() == @cat and test.str.lower() != @cat'
        df = df_melted.query(query)

        # If the query is blank, continue the loop and skip to the next category
        if df.empty:
            continue
        
        # Sort the tests by date
        df.sort_values(by='date',inplace=True,ascending=False)
    
        # Pivot the dataframe so that each date is a column of data and each test has a row
        pivot = df.pivot(index='test', columns='date', values='result')
    
        # Convert column names, which were datetime objects, to dates of type string
        pivot.columns = pivot.columns.strftime('%m/%d/%y')

        # Write the subheader and dataframe to streamlit
        st.subheader(cat.upper())
        st.dataframe(pivot.style.format(precision=1))

        # If any of the tests to plot are in this category, go ahead and plot them
        # Find intersection of the tests we want to plot and the pivot index, which is the 'test' col
        tests_in_cat = set(test.lower() for test in tests_to_plot) & set(test_name.lower() for test_name in pivot.index)
        for test in tests_in_cat:
            fig = tdf.create_plotly_line_plot_of_metric(df_melted,test)
            if fig:
                st.plotly_chart(fig)

# Make styled HTML table
st.markdown('<p>testing</p>',unsafe_allow_html=True)