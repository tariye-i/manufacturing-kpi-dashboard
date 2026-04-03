import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

# Page Config
st.set_page_config(page_title="FGF Production Dashboard", layout="wide")
st.title("Manufacturing Line Dashboard")
st.caption("Real-time production monitoring across Lines A, B, and C")

# Generate Fake Data
def generate_data():
    lines = ["Line A", "Line B", "Line C"]
    data = []
    base_time = datetime.now() - timedelta(hours=24)
    for i in range(48):
        for line in lines:
            data.append({
                "Time": base_time + timedelta(minutes=30 * i),
                "Line": line,
                "Output": random.randint(200, 400),
                "Downtime (mins)": random.randint(0, 15),
                "Efficiency (%)": round(random.uniform(70, 99), 1)
            })
    return pd.DataFrame(data)

df = generate_data()

# Split data into current and previous 12 hour windows for deltas
now = datetime.now()
current_df = df[df["Time"] >= now - timedelta(hours=12)]
previous_df = df[df["Time"] < now - timedelta(hours=12)]

# Sidebar Filters
st.sidebar.header("Filters")
selected_lines = st.sidebar.multiselect(
    "Select Lines",
    ["Line A", "Line B", "Line C"],
    default=["Line A", "Line B", "Line C"]
)
efficiency_threshold = st.sidebar.slider(
    "Efficiency Alert Threshold (%)", 
    min_value=50, 
    max_value=95, 
    value=80
)

filtered_df = df[df["Line"].isin(selected_lines)]
filtered_current = current_df[current_df["Line"].isin(selected_lines)]
filtered_previous = previous_df[previous_df["Line"].isin(selected_lines)]

# KPI Cards with deltas
st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3)

current_output = filtered_current["Output"].sum()
previous_output = filtered_previous["Output"].sum()
output_delta = current_output - previous_output

current_efficiency = round(filtered_current["Efficiency (%)"].mean(), 1)
previous_efficiency = round(filtered_previous["Efficiency (%)"].mean(), 1)
efficiency_delta = round(current_efficiency - previous_efficiency, 1)

current_downtime = filtered_current["Downtime (mins)"].sum()
previous_downtime = filtered_previous["Downtime (mins)"].sum()
downtime_delta = current_downtime - previous_downtime

col1.metric("Total Output (Last 12hrs)", f"{current_output:,} units", delta=f"{output_delta:,} vs previous 12hrs")
col2.metric("Avg Efficiency (Last 12hrs)", f"{current_efficiency}%", delta=f"{efficiency_delta}% vs previous 12hrs")
col3.metric("Total Downtime (Last 12hrs)", f"{current_downtime} mins", delta=f"{downtime_delta} mins vs previous 12hrs", delta_color="inverse")

st.divider()

# Alerts Panel
st.subheader("Alerts")
low_efficiency = filtered_df[filtered_df["Efficiency (%)"] < efficiency_threshold]

if low_efficiency.empty:
    st.success("All lines operating above efficiency threshold.")
else:
    alert_summary = low_efficiency.groupby("Line").size().reset_index(name="Incidents")
    for _, row in alert_summary.iterrows():
        st.warning(f"{row['Line']}: {row['Incidents']} readings below {efficiency_threshold}% efficiency threshold")

st.divider()

# Charts
col4, col5 = st.columns(2)

with col4:
    st.subheader("Output Over Time")
    fig1 = px.line(filtered_df, x="Time", y="Output", color="Line")
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.subheader("Downtime by Line")
    fig2 = px.bar(
        filtered_df.groupby("Line")["Downtime (mins)"].sum().reset_index(),
        x="Line",
        y="Downtime (mins)",
        color="Line"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Efficiency Over Time")
fig3 = px.line(filtered_df, x="Time", y="Efficiency (%)", color="Line")
fig3.add_hline(
    y=efficiency_threshold, 
    line_dash="dash", 
    line_color="red", 
    annotation_text="Alert Threshold"
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Raw Data Table
st.subheader("Raw Readings")
st.dataframe(
    filtered_df.sort_values("Time", ascending=False).reset_index(drop=True),
    use_container_width=True
)