import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from datetime import datetime
from scipy.integrate import trapz, simps
from scipy.signal import savgol_filter
import seaborn as sns
import os

mpl.rcParams['font.family'] = 'Avenir'

# Function to convert time to minutes since midnight
def time_to_minutes(t):
    return t.hour * 60 + t.minute

def read_cgm_csv(filepath):
    # Ingest the CSV into a pandas DataFrame
    csv_file = ""
    csv_file_basename = os.path.basename(csv_file)
    global csv_file_dirname = os.path.dirname(csv_file)

    ptname = os.path.basename(csv_file).split('%')[0].split('_')[2:4]
    ptname = ','.join(ptname)
    df = pd.read_csv(csv_file, parse_dates=[1])

    # Extract the datetime and glucose columns
    df = df.iloc[:, [1, 7]]
    df.columns = ["Datetime", "Glucose"]

    df = df.dropna(subset=['Datetime'])

    # Find date range
    min_date = df['Datetime'].min()
    max_date = df['Datetime'].max()
    date_range = f"{min_date.strftime('%m/%d/%Y')} to {max_date.strftime('%m/%d/%Y')}"

    # Convert Glucose to numeric type (in case it's stored as strings)
    df['Glucose'] = pd.to_numeric(df['Glucose'], errors='coerce')

    # Extract just the time component and convert to minutes since midnight
    df['Minutes'] = df['Datetime'].dt.time.apply(time_to_minutes)

    # Removing extreme outliers using IQR method for each minute group
    def remove_outliers(group):
        Q1 = group['Glucose'].quantile(0.34)
        Q3 = group['Glucose'].quantile(0.68)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return group[(group['Glucose'] >= lower_bound) & (group['Glucose'] <= upper_bound)]

    df = df.groupby('Minutes').apply(remove_outliers).reset_index(drop=True)
    return df

def calc_smoothed_quantiles(df):
    # Calculate the quantiles for each minute after outlier removal and interpolation
    grouped = df.groupby('Minutes').Glucose
    quantiles = grouped.quantile([0.10, 0.34, 0.50, 0.68, 0.90]).unstack()

    # Padding the start and end of the quantiles DataFrame
    window_size = 20
    pad_size = window_size // 2
    start_padding = pd.DataFrame([quantiles.iloc[0]] * pad_size, columns=quantiles.columns, index=[-i-1 for i in range(pad_size)][::-1])
    end_padding = pd.DataFrame([quantiles.iloc[-1]] * pad_size, columns=quantiles.columns, index=[i+quantiles.index[-1]+1 for i in range(pad_size)])

    #padded_quantiles = pd.concat([start_padding, quantiles, end_padding])

    # Applying a moving average to smooth the data
    #smoothed_padded_quantiles = padded_quantiles.rolling(window=window_size, center=True).mean()
    #smoothed_quantiles = smoothed_padded_quantiles.iloc[pad_size:-pad_size]

    #smoothed_quantiles = quantiles.rolling(window=window_size, center=True).mean()
    #smoothed_quantiles.interpolate(method='linear', inplace=True)


    # Applying the Savitzky-Golay filter to smooth the data
    window_size = 111  # Should be odd
    poly_order = 2  # Polynomial order for the filter

    # Applying the filter for each quantile
    smoothed_quantiles = quantiles.copy()
    minutes_mask = df.groupby('Minutes').size().reindex(range(0, 1440)).notna()
    quantiles = quantiles[minutes_mask]

    for col in smoothed_quantiles.columns:
        smoothed_quantiles[col] = savgol_filter(quantiles[col], window_size, poly_order)
    return smoothed_quantiles

# Define color gradients based on the hex colors you provided
night_color = np.array([0, 32, 128]) / 255.
daytime_color = np.array([255, 223, 186]) / 255.   # A yellow daylight color
sunrise_middle = np.array([38, 125, 255]) / 255.   # #267DFF
sunset_middle = np.array([218, 89, 85]) / 255.    # #DA5955

def interpolate_colors(colors, num):
    """Generate interpolated color values."""
    r_diff = colors[1, 0] - colors[0, 0]
    g_diff = colors[1, 1] - colors[0, 1]
    b_diff = colors[1, 2] - colors[0, 2]

    r = np.linspace(colors[0, 0], colors[0, 0] + r_diff, num)
    g = np.linspace(colors[0, 1], colors[0, 1] + g_diff, num)
    b = np.linspace(colors[0, 2], colors[0, 2] + b_diff, num)

    return list(zip(r, g, b))

def plot_and_save(df):
    plt.figure(figsize=(15, 8))
    ax = plt.gca()

    # Shade background using gradient
    periods = [(300, 370, [night_color, sunrise_middle]),
            (370, 440, [sunrise_middle, daytime_color]),
            (440, 1100, [daytime_color, daytime_color]),
            (1100, 1200, [daytime_color, sunset_middle]),
            (1200, 1300, [sunset_middle, night_color]),
            (0, 300, [night_color, night_color]), 
            (1300, 1440, [night_color, night_color])]

    for start, end, colors in periods:
        gradient = interpolate_colors(np.array(colors), end-start)
        for i, color in enumerate(gradient):
            ax.axvspan(start+i, start+i+1, facecolor=color, alpha=0.40)


    # Plot the median glucose level
    plt.plot(smoothed_quantiles.index, smoothed_quantiles[0.5], label='Mean', color='#267DFF', alpha=0.75, linewidth=2)

    # Shaded areas for the quantiles
    #plt.fill_between(smoothed_quantiles.index, smoothed_quantiles[0.10], smoothed_quantiles[0.90], color='gray', alpha=0.1, label='10th-90th Percentile')
    #plt.fill_between(smoothed_quantiles.index, smoothed_quantiles[0.34], smoothed_quantiles[0.68], color='gray', alpha=0.3, label='Mean +/- St.dev')

    # Mask values below 100 for the 75th percentile
    mask_above_100 = smoothed_quantiles[0.68] > 100

    # Use the masked values to calculate the area
    area_above_100 = np.trapz(smoothed_quantiles[0.68][mask_above_100] - 100, dx=1)


    # Shade the area between the 75th percentile curve and the 100 mg/dL line
    plt.fill_between(smoothed_quantiles.index, 
                    np.where(smoothed_quantiles[0.68] > 100, smoothed_quantiles[0.68], 100), 
                    100, 
                    where=smoothed_quantiles[0.68] > 100, 
                    color='grey', alpha=0.45, label='Area between +1 St.dev and 100 mg/dL')

    # Adding the swarm plot
    #sns.swarmplot(x=df['Minutes'], y=df['Glucose'], color="#FF8C69", size=1.5, alpha=0.25)



    # Add horizontal lines at specific glucose levels
    plt.axhline(y=90, color='grey', linestyle='--', alpha=0.5)
    plt.axhline(y=100, color='green', linestyle='-', alpha=0.5)
    plt.axhline(y=110, color='yellow', linestyle='--', alpha=0.5)
    plt.axhline(y=140, color='red', linestyle='--', alpha=0.5)


    # Formatting the x-ticks to display time
    plt.xticks(ticks=[i for i in range(0, 24*60+1, 60)], 
            labels=[f'{i:02}:00' for i in range(25)], 
            rotation=45)

    ax.set_xlim(left=smoothed_quantiles.index.min(), right=smoothed_quantiles.index.max())

    # Calculate the portions of the 25th and 75th percentile curves that are above 100 mg/dL
    diff_25_above_100 = np.maximum(smoothed_quantiles[0.34].values - 100, 0)
    diff_75_above_100 = np.maximum(smoothed_quantiles[0.68].values - 100, 0)
    #print(diff_25_above_100,diff_75_above_100)
    # Calculate the AUC between the two curves, considering only the portions above 100 mg/dL
    auc_between_curves = np.trapz(diff_75_above_100 - diff_25_above_100, smoothed_quantiles.index.values)

    #print(f"This is currently wrong: AUC between 25th and 75th percentile curves above 100 mg/dL: {auc_between_curves:.2f}")

    # Plot the line for max values
    max_values = df.groupby('Minutes').Glucose.max()
    df_max = df.groupby('Minutes').Glucose.max().reset_index()
    df_max.columns = ['Minutes', 'Glucose']
    df_max = df_max.groupby('Minutes').apply(remove_outliers).reset_index(drop=True)
    #df_max['Glucose'].interpolate(method='linear', inplace=True)
    # Calculate the number of values you need to pad (half of the window size)
    # Pad the front and end of the dataset with replicated data
    #padded_data = pd.concat([df_max['Glucose'].head(pad_size).iloc[::-1], df_max['Glucose'], df_max['Glucose'].tail(pad_size).iloc[::-1]])
    #smoothed_max_padded = padded_data.rolling(window=20, center=True).max()

    savgol_data = savgol_filter(df_max['Glucose'], window_length=window_size, polyorder=poly_order)
    #smoothed_max = smoothed_max_padded.iloc[pad_size:-pad_size].reset_index(drop=True)
    plt.plot(df_max['Minutes'], savgol_data, label='Smoothed Maximum', color='red', alpha=0.25, linewidth=2, linestyle='--')


    #plt.title("Smoothed Glucose Readings Quantiles Throughout the Day (Outliers Removed)")
    plt.xlabel("Time of Day")
    plt.ylabel("Glucose (mg/dL)")
    plt.legend(loc='upper left', bbox_to_anchor=(0, 1))

    plt.tight_layout()
    title=f"{ptname} | {date_range} | CGM Readings | Smoothed over {window_size} minute windows using Savitzky-Golay Smoothing"
    plt.title(title, weight='bold')

    plt.subplots_adjust(top=0.90)  # Adjust the top spacing to 90% of the figure height


    dates = date_range.replace(' ','_').replace('/','.')
    outfile = f"{csv_file_dirname}/{ptname}_cgm_plot_{dates}.png"
    plt.savefig(outfile, dpi=300)

    plt.show()

def make_plot_from_cgm_csv(path):
    df = read_cgm_csv(path)
    df = calc_smoothed_quantiles(df)
    plot_and_save(df)