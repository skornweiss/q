import streamlit as st
import pandas as pd
from io import StringIO

import trends_dataframe_functions as tdf
from datetime import date
from trends_constants import *

st.echo(categories)

# App Title
st.title("Coconut")

# Dash
st.metric("Date", date.ctime(date.today()))

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
    #df = tdf.sort_columns_reverse_chronological(df)
    df = tdf.id_category_rows(df)
    #styled_df = df.style.set_sticky(axis=1)
    styled_df = df.style.format(precision=2,)
    cat_rows = df.index[df['is_category'] == True].tolist()
    styled_df = styled_df.set_properties(subset=pd.IndexSlice[cat_rows,:],**{'background-color':'black','color':'white'})
    styled_df
    df.rename(columns={df.columns[0]:'test'},inplace=True)
    df_melted = pd.melt(df,id_vars=[df.columns[0]],value_name="result",var_name="date")
    df_melted = tdf.add_category_column(df_melted,categories)
    df_melted = df_melted.query('category == "Lipids" and test != "Lipids"')
    df_melted
    df_melted.sort_values(by='date',inplace=True)
    st.line_chart(df_melted,x='date',y='result')