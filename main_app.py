import streamlit as st
import pandas as pd
from io import StringIO
from dateutil.parser import parse
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


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
    #df = tdf.sort_columns_reverse_chronological(df)
    df = tdf.id_category_rows(df)
    #st.table(df)
    #st.markdown(df.to_markdown())
    #styled_df = df.style.set_sticky(axis=1)
    styled_df = df.style.format(precision=2,)
    cat_rows = df.index[df['is_category'] == True].tolist()
    styled_df = styled_df.set_properties(subset=pd.IndexSlice[cat_rows,:],**{'background-color':'black','color':'white'})
    #styled_df
    df.rename(columns={df.columns[0]:'test'},inplace=True)
    df_melted = pd.melt(df,id_vars=[df.columns[0]],value_name="result",var_name="date")
    df_melted = tdf.add_category_column(df_melted,categories)
    df_melted = df_melted.query('date !="is_category"')
    df_melted["date"] = pd.to_datetime(df_melted["date"])
    for category in categories:
        cat = category.capitalize()
        query = f'category == "{cat}" and test != "{cat}"'
        df = df_melted.query(query)       
        df.sort_values(by='date',inplace=True,ascending=False)
        #df
        #df = df.iloc[::-1]
        if df.empty:
            continue
        pivot = df.pivot(index='test', columns='date', values='result') #.drop(['is_category'],axis=1)
        #pivot = pivot.reindex(columns=pivot.columns[::-1])
        pivot.columns = pivot.columns.strftime('%m/%d/%y')
        st.subheader(cat.upper())
        st.dataframe(pivot)
        if cat.lower() == 'lipoproteins':
            df1 = df.query('test == "ApoB"')
            print(df1)
            df1.sort_values(by='date',ascending=False,inplace=True)
            fig = px.line(df1, x='date', y='result', title='ApoB')
            fig.update_xaxes(tickmode='array',tickvals=df1['date'],tickformat="%m/%d/%y")
            # Add data labels to each point
            for x, y in zip(df1['date'], df1['result']):
                fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers', marker=dict(color='black', size=6), showlegend=False))
                fig.add_annotation(x=x, y=y, text=str(y), showarrow=False, yshift=12, xshift=5, font=dict(color="black"))
            st.plotly_chart(fig)
        if cat.lower() == 'sex hormones':
            df2 = df.query('test == "PSA"').replace('',np.nan).dropna()
            if df2.empty:
                continue
            print(df2)
            df2.sort_values(by='date',inplace=True)
            fig2 = px.line(df2, x='date', y='result', title="PSA")
            fig2.update_xaxes(tickmode='array',tickvals=df2['date'],tickformat="%m/%d/%y")
            # Add data labels to each point
            for x, y in zip(df2['date'], df2['result']):
                fig2.add_trace(go.Scatter(x=[x], y=[y], mode='markers', marker=dict(color='black', size=6), showlegend=False))
                fig2.add_annotation(x=x, y=y, text=str(y), showarrow=False, yshift=12, xshift=5, font=dict(color="black"))
            st.plotly_chart(fig2)
        if cat.lower() == 'sex hormones':
            df3 = df.query('test == "Free testosterone"').replace('',np.nan).dropna()
            print(df3)
            df3.sort_values(by='date',inplace=True)
            fig = px.line(df3, x='date', y='result', title="Free T")
            fig.update_xaxes(tickmode='array',tickvals=df3['date'],tickformat="%m/%d/%y")
            # Add data labels to each point
            for x, y in zip(df3['date'], df3['result']):
                fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers', marker=dict(color='black', size=6), showlegend=False))
                fig.add_annotation(x=x, y=y, text=str(y), showarrow=False, yshift=12, xshift=5, font=dict(color="black"))
            st.plotly_chart(fig)
