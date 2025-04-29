
import pandas as pd
import plotly.express as px
import streamlit as st

# Load the merged data
merged_df = pd.read_csv('merged_bee_data_2022_2023_2024.csv')

# Streamlit app
def main():
    st.title("Bee Campaign Performance Dashboard (2022-2024)")
    st.markdown("### Quick Overview")

    # Sidebar Filters
    year_options = ['2022', '2023', '2024']
    selected_year = st.sidebar.selectbox("Select Year", year_options)

    # Filter columns based on selected year
    spend_col = f"Spend {selected_year}"
    impressions_col = f"Impressions {selected_year}"
    clicks_col = f"Clicks {selected_year}"

    # Filter Data
    filtered_df = merged_df[["Date", spend_col, impressions_col, clicks_col]].dropna()
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

    # Metrics
    total_spend = filtered_df[spend_col].replace('[\\$,]', '', regex=True).astype(float).sum()
    total_impressions = filtered_df[impressions_col].replace('[,]', '', regex=True).astype(float).sum()
    total_clicks = filtered_df[clicks_col].replace('[,]', '', regex=True).astype(float).sum()

    st.metric("Total Spend", f"${total_spend:,.2f}")
    st.metric("Total Impressions", f"{total_impressions:,.0f}")
    st.metric("Total Clicks", f"{total_clicks:,.0f}")

    # Line chart for Spend over Time
    st.markdown("### Spend Over Time")
    fig_spend = px.line(
        filtered_df,
        x='Date',
        y=spend_col,
        title=f"Daily Spend - {selected_year}",
        labels={spend_col: 'Spend ($)'}
    )
    st.plotly_chart(fig_spend)

    # Line chart for Impressions over Time
    st.markdown("### Impressions Over Time")
    fig_impressions = px.line(
        filtered_df,
        x='Date',
        y=impressions_col,
        title=f"Daily Impressions - {selected_year}",
        labels={impressions_col: 'Impressions'}
    )
    st.plotly_chart(fig_impressions)

    # Line chart for Clicks over Time
    st.markdown("### Clicks Over Time")
    fig_clicks = px.line(
        filtered_df,
        x='Date',
        y=clicks_col,
        title=f"Daily Clicks - {selected_year}",
        labels={clicks_col: 'Clicks'}
    )
    st.plotly_chart(fig_clicks)

if __name__ == "__main__":
    main()
