import streamlit as st
import pandas as pd
from io import StringIO
from dateutil.parser import parse
import re
import pyperclip
import statistics

import trends_dataframe_functions as tdf
from datetime import date
from trends_constants import categories, tests_to_plot
import make_trends_pretty as mtp
import blood_pressure_analytics as bpa
import cgm_plot as cgm

# streamlit_app.py

import hmac
import streamlit as st


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

# Begin App

st.echo(categories)

# App Title
#st.title("EMERPA")
#st.write('Early Medical Extremely Robust and Perfect Analytics')
#st.divider()

# Dash
#st.metric("Date", date.ctime(date.today()))

# Sidebar
# Add file-uploader to sidebar
trends_file = st.sidebar.file_uploader('Upload Trends File', help="Select an excel lab trends sheet")
#bp_file = st.sidebar.file_uploader('Upload BP File')
psa_vol = st.sidebar.number_input('PSA Volume')

a = pd.DataFrame()
#a.style.format(precision=2,hidd)

if trends_file is not None:

    pretty_trends_html = mtp.main(trends_file)
    st.sidebar.download_button('Download Pretty Trends', pretty_trends_html, file_name="pretty_trends.html")
        
    df = pd.read_excel(trends_file, parse_dates=True, header=None, index_col=None)
    df = tdf.clean_trends_df(df)
    df = tdf.validate_headers(df)
    df = tdf.format_date_headers(df)
    
    # Adds 'is_category' column set to True for rows that are category rows
    df = tdf.id_category_rows(df)

    # Convert all numeric columns to float
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
        
    # Example of how to style float precision for display
    #styled_df = df.style.format(precision=2)
    #styled_df

    # Identifies category rows and puts them into a list for styling
    #cat_rows = df.index[df['is_category'] == True].tolist()
    #styled_df = styled_df.set_properties(subset=pd.IndexSlice[cat_rows,:],**{'background-color':'black','color':'white'})
    #styled_df

    # Get name in case we want it, but then immediately over-write if not using
    patient_name = df.columns[0]
    if patient_name:
        st.header(patient_name)
        st.divider()
    patient_name = '4;tqoiheg;iheg;43htq34d;lkj'
    del(patient_name)
    df.rename(columns={df.columns[0]:'test'},inplace=True)
    df_melted = pd.melt(df,id_vars=[df.columns[0]],value_name="result",var_name="date")
    df_melted = tdf.add_category_column(df_melted,categories)
    df_melted_nocat = df_melted.query('date !="is_category"')
    df_melted_nocat = df_melted_nocat.copy()
    #df_melted_nocat["date"] = pd.to_datetime(df_melted_nocat["date"], format='%m/%d/%Y', errors='coerce')
    df_melted_nocat["date"] = pd.to_datetime(df_melted_nocat["date"],errors='ignore')
        
    # Make tables to display the dataframe for each category of test separately
    for cat in categories:
    
        # Query the larger dataframe for tests that fall into a specific category
        query = 'category.str.lower() == @cat and test.str.lower() != @cat'
        df = df_melted_nocat.query(query)

        # If the query is blank, continue the loop and skip to the next category
        if df.empty:
            continue
        
        # Sort the tests by date
        df = df.sort_values(by='date', ascending=False)
    
        # Pivot the dataframe so that each date is a column of data and each test has a row
        pivot = df.pivot(index='test', columns='date', values='result')
    
        # Convert column names, which were datetime objects, to dates of type string
        pivot.columns = pivot.columns.strftime('%m/%d/%y')
        pivot = pivot.reset_index()

        # Write the subheader and dataframe to streamlit
        st.subheader(cat.upper(),divider=True)
        st.dataframe(pivot.style.format(precision=1).apply(tdf.zebra_striping),hide_index=True)

        # If any of the tests to plot are in this category, go ahead and plot them
        # Find intersection of the tests we want to plot and the pivot index, which is the 'test' col
        tests_in_cat = set(test.lower() for test in tests_to_plot) & set(test_name.lower() for test_name in pivot['test'])
        for test in tests_in_cat:
            fig = tdf.create_plotly_line_plot_of_metric(df_melted_nocat,test)
            if fig:
                st.plotly_chart(fig)
            if test == 'psa' and psa_vol:
                #print(df_melted[df_melted['test'].str.lower() == "psa"])
                psa_df = df_melted_nocat.query('test.str.lower() == "psa"')
                psa_df = psa_df[psa_df['result'] != '']
                psa_df['date'] = pd.to_datetime(psa_df['date'])
                
                # Find the row with the most recent date
                most_recent_row = psa_df.loc[psa_df['date'].idxmax()]
                
                # Select the 'result' from the most recent row
                most_recent_psa = most_recent_row['result']
                most_recent_psa_date = most_recent_row['date'].strftime("%m.%d.%y")
                

                #most_recent_psa = df_melted[df_melted['test'].str.lower() == "psa"].sort_values('date', ascending=False).iloc[1]['result']
                #most_recent_psa_date = df_melted[df_melted['test'].str.lower() == "psa"].sort_values('date', ascending=False).iloc[1]['date']
                
                psa_density = float(float(most_recent_psa) / psa_vol)
                st.write(f"Most recent PSA: {most_recent_psa} ({most_recent_psa_date})")
                st.write(f"PSA Density: {psa_density:.2}")
                st.sidebar.write(f"Most recent PSA: {most_recent_psa} ({most_recent_psa_date})")
                st.sidebar.write(f"PSA Density: {psa_density:.2}")
        st.divider()

    # Display pretty trends within the app
    #st.markdown(pretty_trends_html,unsafe_allow_html=True)

#if bp_file is not None:
#    pass


cgm_csv = st.sidebar.file_uploader('Upload CGM CSV')
if cgm_csv is not None:
    plot = cgm.create_cgm_plot(cgm_csv)
    st.pyplot(plot)


if st.sidebar.button('Analyze BPs on Clipboard'):
    try:
        clipboard = pyperclip.paste()

        
        bp_pattern = r'\b\d{2,3}/\d{2,3}\b'
        # Find all matching patterns in the text
        matches = re.findall(bp_pattern, clipboard)
        
        # Convert the matched readings to integers for processing
        readings = [tuple(map(int, match.split('/'))) for match in matches]

        # Calculate the mean of systolic and diastolic pressures separately
        systolic_values = [reading[0] for reading in readings]
        diastolic_values = [reading[1] for reading in readings]

        # Calculate the mean values for systolic and diastolic pressures
        mean_systolic = statistics.mean(systolic_values)
        mean_diastolic = statistics.mean(diastolic_values)

        # Calculate the threshold for outliers
        threshold_systolic = mean_systolic * 0.5
        threshold_diastolic = mean_diastolic * 0.5

        # Filter out outliers
        filtered_readings = [match for match in matches if all(
            abs(int(val) - mean) <= threshold
            for val, mean, threshold in zip(match.split('/'), [mean_systolic, mean_diastolic], [threshold_systolic, threshold_diastolic])
        )]
        bpdf = pd.DataFrame(filtered_readings)
        #bpdf = pd.read_clipboard() #header=None) #,sep=',',quotechar=':')
        #bpdf
        bpdf.columns = ['BPs']
        st.markdown(bpdf.to_markdown())
        fig = bpa.create_plotly_bp_fig(bpdf)
        st.plotly_chart(fig)
    except:
        raise
    

st.sidebar.file_uploader('upload new file')