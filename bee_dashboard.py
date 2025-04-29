
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Load the merged data
merged_df = pd.read_csv('merged_bee_data_2022_2023_2024.csv')

# Normalize dates
merged_df['Date'] = pd.to_datetime(merged_df['Date'], errors='coerce')
merged_df['MonthDay'] = merged_df['Date'].dt.strftime('%m-%d')
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
        temp = merged_df[['MonthDay', metric_cols[idx]]].copy()
        temp.columns = ['MonthDay', 'Value']
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
        temp = df[['MonthDay', f'Combined {year}']].copy()
        temp.columns = ['MonthDay', 'Value']
        temp['Year'] = year
        temp['Metric'] = 'Combined Conversion'
        data = pd.concat([data, temp], axis=0)
    return data

# Merge all data
data_frames = []
for metric, cols in metrics.items():
    data_frames.append(prepare_metric(cols, metric))

data_frames.append(prepare_combined_conversion())

full_data = pd.concat(data_frames, axis=0)

# Streamlit app
def main():
    st.title("Bee Campaign Dashboard (2022-2024)")

    selected_metric = st.radio(
        "Select Metric to View",
        ['Leads', 'Purchases', 'CPL', 'CPA', 'Combined Conversion']
    )

    group_by = st.radio(
        "Group Data By",
        ['Day', 'Week', 'Month']
    )

    show_2022 = st.checkbox('Show 2022', value=True)
    show_2023 = st.checkbox('Show 2023', value=True)
    show_2024 = st.checkbox('Show 2024', value=True)

    chart_data = full_data[full_data['Metric'] == selected_metric]

    if group_by == 'Week':
        chart_data['Week'] = pd.to_datetime('2024-' + chart_data['MonthDay']).dt.isocalendar().week
        x_col = 'Week'
    elif group_by == 'Month':
        chart_data['Month'] = pd.to_datetime('2024-' + chart_data['MonthDay']).dt.month
        x_col = 'Month'
    else:
        x_col = 'MonthDay'

    fig = go.Figure()

    color_mapping = {
        2022: 'lightblue',
        2023: 'dodgerblue',
        2024: 'navy'
    }

    for year in [2022, 2023, 2024]:
        if (year == 2022 and show_2022) or (year == 2023 and show_2023) or (year == 2024 and show_2024):
            year_data = chart_data[chart_data['Year'] == year]
            fig.add_trace(go.Scatter(
                x=year_data[x_col],
                y=year_data['Value'],
                mode='markers',
                name=str(year),
                marker=dict(color=color_mapping[year])
            ))

    fig.update_layout(
        title=f"{selected_metric} Over Time",
        xaxis_title=x_col,
        yaxis_title=selected_metric,
        legend_title="Year",
        height=600
    )

    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
