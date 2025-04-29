import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LinearRegression
import numpy as np

# Load the merged data
merged_df = pd.read_csv('merged_bee_data_2022_2023_2024.csv')

# Normalize dates to day-of-year for year-over-year comparisons
merged_df['Date'] = pd.to_datetime(merged_df['Date'], errors='coerce')
merged_df['DayOfYear'] = merged_df['Date'].dt.dayofyear
merged_df['Year'] = merged_df['Date'].dt.year

# Extract relevant columns
metrics = {
    'Leads': ['Web Attributed Leads 2022', 'Web Attributed Leads 2023', 'Web Attributed Leads 2024'],
    'Purchases': ['Web Attributed Joins 2022', 'Web Attributed Joins 2023', 'Web Attributed Joins 2024'],
    'CPL': ['CPL 2022', 'CPL 2023', 'CPL 2024'],
    'CPA': ['CPA 2022', 'CPA 2023', 'CPA 2024']
}

# Prepare data
def prepare_metric(metric_cols, label):
    data = pd.DataFrame()
    for idx, year in enumerate([2022, 2023, 2024]):
        temp = merged_df[['DayOfYear', metric_cols[idx]]].copy()
        temp.columns = ['DayOfYear', 'Value']
        temp['Year'] = year
        temp['Metric'] = label
        data = pd.concat([data, temp], axis=0)
    return data

# Combined leads + joins
def prepare_combined_conversion():
    df = merged_df.copy()
    for year in [2022, 2023, 2024]:
        df[f'Combined {year}'] = df.get(f'Web Attributed Leads {year}', 0) + df.get(f'Web Attributed Joins {year}', 0)
    data = pd.DataFrame()
    for year in [2022, 2023, 2024]:
        temp = df[['DayOfYear', f'Combined {year}']].copy()
        temp.columns = ['DayOfYear', 'Value']
        temp['Year'] = year
        temp['Metric'] = 'Combined Conversion'
        data = pd.concat([data, temp], axis=0)
    return data

# Build projections for 2025
def build_projection(df):
    projected_data = []
    for metric in df['Metric'].unique():
        metric_df = df[df['Metric'] == metric]
        X = metric_df['DayOfYear'].values.reshape(-1, 1)
        y = metric_df['Value'].replace('[\$,]', '', regex=True).replace(',', '', regex=True)
        y = pd.to_numeric(y, errors='coerce').fillna(0)
        model = LinearRegression().fit(X, y)
        days_2025 = np.arange(1, 366).reshape(-1,1)
        preds = model.predict(days_2025)
        temp = pd.DataFrame({
            'DayOfYear': days_2025.flatten(),
            'Value': preds,
            'Year': 2025,
            'Metric': metric
        })
        projected_data.append(temp)
    return pd.concat(projected_data, axis=0)

# Merge all data
data_frames = []
for metric, cols in metrics.items():
    data_frames.append(prepare_metric(cols, metric))

data_frames.append(prepare_combined_conversion())

full_data = pd.concat(data_frames, axis=0)
projection_data = build_projection(full_data)
full_data = pd.concat([full_data, projection_data], axis=0)

# Streamlit app
def main():
    st.title("Bee Campaign Dashboard (2022-2025 Projection)")

    selected_metric = st.selectbox(
        "Select Metric to View",
        ['Leads', 'Purchases', 'CPL', 'CPA', 'Combined Conversion']
    )

    chart_data = full_data[full_data['Metric'] == selected_metric]

    fig = go.Figure()

    color_mapping = {
        2022: 'lightblue',
        2023: 'dodgerblue',
        2024: 'navy',
        2025: 'gray'
    }
    line_style = {
        2022: 'solid',
        2023: 'solid',
        2024: 'solid',
        2025: 'dash'
    }

    for year in [2022, 2023, 2024, 2025]:
        year_data = chart_data[chart_data['Year'] == year]
        fig.add_trace(go.Scatter(
            x=year_data['DayOfYear'],
            y=year_data['Value'],
            mode='lines',
            name=str(year),
            line=dict(color=color_mapping[year], dash=line_style[year])
        ))

    fig.update_layout(
        title=f"{selected_metric} Over Time (2022-2025)",
        xaxis_title="Day of Year",
        yaxis_title=selected_metric,
        legend_title="Year",
        height=600
    )

    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
