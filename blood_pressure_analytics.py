import plotly.graph_objects as go
import pandas as pd
import re

# Sample DataFrame (replace this with your actual data)
"""df = pd.DataFrame({
    'Column1': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
    'Column2': ['120/80', '130/85', '110/75', '115/78', '118/76'],
    'Column3': ['Random', 'Data', 'Here', 'Not', 'Relevant']
})"""

def check_for_time_data(series, threshold=0.5):
    """Check if a significant portion of a series can be converted to datetime."""
    count = 0
    for item in series:
        try:
            pd.to_datetime(item)
            count += 1
        except:
            continue
    return count / len(series) >= threshold

def is_bp_format(s):
    """Check if a string is in blood pressure format 'number/number'."""
    return bool(re.match(r'^\d+/\d+$', s))

def clean_bp(s):
     # Use regular expression to remove unwanted characters
    cleaned_bp = re.sub(r'[^\d\/]', '', s)
    
    # Optionally, you can add validation to check if the cleaned result is in the correct format
    if not re.match(r'^\d+/\d+$', cleaned_bp):
        # Handle invalid format (e.g., return None or raise an exception)
        return None

    return cleaned_bp


def filter_bp_data(df):
    # Create a mask for blood pressure data
    df = df.map(lambda x: clean_bp(x))
    bp_mask = df.map(lambda x: is_bp_format(str(x)))

    # Use the mask to filter rows and columns
    filtered_df = df.loc[bp_mask.any(axis=1), bp_mask.any(axis=0)]

    return filtered_df

def create_plotly_bp_fig(df):
    df = filter_bp_data(df)
    
    # Find the time and blood pressure columns
    time_column = None
    bp_column = None

    for col in df.columns:
        # Check for time data
        if check_for_time_data(df[col]):
            time_column = col
        # Check for blood pressure data
        elif any(is_bp_format(str(x)) for x in df[col]):
            bp_column = col

        if time_column and bp_column:
            break

    # Process the time column if found
    if time_column:
        df[time_column] = pd.to_datetime(df[time_column], errors='coerce')
        x_axis = df[time_column]
        x_title = "Time"
    else:
        x_axis = df.index
        x_title = "Index"
    
    # Split the blood pressure data into systolic and diastolic
    if bp_column is not None:
        df[['systolic', 'diastolic']] = df[bp_column].str.split('/', expand=True).astype(float)
    

        # Calculate midpoints and heights
        df['mid'] = (df['systolic'] + df['diastolic']) / 2
        df['height'] = df['systolic'] - df['diastolic']
        bar_width = 0.5
        # Create a Bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x_axis,
            y=df['systolic'] - df['diastolic'],
            base=df['diastolic'],
            name='Blood Pressure Range',
            orientation='v',
            width=bar_width,
            showlegend=False,
            marker=dict(
            color='#2e5090',  # This acts as a mask
            opacity=0.5  # Almost fully transparent
            )))

        # Calculate the average systolic and diastolic values
        avg_systolic = df['systolic'].mean()
        std_systolic = df['systolic'].std()
        avg_diastolic = df['diastolic'].mean()
        std_diastolic = df['diastolic'].std()


        # Add line trace for average systolic value
        fig.add_trace(go.Scatter(
            #x=df['Date'],
            y=[avg_systolic] * len(df),
            mode='lines',
            line=dict(color='#F36A65', width=2, dash='dash'),
            name=f'Avg Systolic: {avg_systolic:.0f} +/- {std_systolic:.0f}'
        ))

        # Add line trace for average diastolic value
        fig.add_trace(go.Scatter(
            #x=df['Date'],
            y=[avg_diastolic] * len(df),
            mode='lines',
            line=dict(color='#3E8BFF', width=2, dash='dash'),
            name=f'Avg Diastolic: {avg_diastolic:.0f} +/- {std_diastolic:.0f}'
        ))

        # Update layout
        fig.update_layout(
            title="Blood Pressure Readings with Averages",
            #xaxis_title="Date",
            yaxis_title="Blood Pressure (mmHg)"
        )
       

        # Update layout
        fig.update_layout(
            title="Blood Pressure Readings",
            xaxis_title=x_title,
            yaxis_title="Blood Pressure (mmHg)",
            legend=dict(
            font=dict(
                size=18,  # Set the font size here
                family="Avenir"                
            ),
            x=0.5,
            y=1.2,
            bgcolor='rgba(0,0,0,0)'
        ))
        return fig
    # Show the plot
    #fig.show()
