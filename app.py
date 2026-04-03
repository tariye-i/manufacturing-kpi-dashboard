import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
from scipy import stats

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
            output = random.randint(200, 400)
            if random.random() < 0.08:
                output = random.randint(50, 150)
            efficiency = round(random.uniform(70, 99), 1)
            if random.random() < 0.08:
                efficiency = round(random.uniform(30, 55), 1)
            data.append({
                "Time": base_time + timedelta(minutes=30 * i),
                "Line": line,
                "Output": output,
                "Downtime (mins)": random.randint(0, 15),
                "Efficiency (%)": efficiency
            })
    return pd.DataFrame(data)

df = generate_data()

# Detect anomalies using Z-score
def detect_anomalies(data, column, threshold=2.0):
    z_scores = stats.zscore(data[column])
    data = data.copy()
    data["Z-Score"] = z_scores
    data["Anomaly"] = abs(z_scores) > threshold
    return data

# Generate shift report text
def generate_shift_report(shift_df, anomalies, efficiency_threshold):
    worst_line = shift_df.groupby("Line")["Efficiency (%)"].mean().idxmin()
    worst_efficiency = round(shift_df.groupby("Line")["Efficiency (%)"].mean().min(), 1)
    total_output = shift_df["Output"].sum()
    avg_efficiency = round(shift_df["Efficiency (%)"].mean(), 1)
    total_downtime = shift_df["Downtime (mins)"].sum()
    anomaly_count = len(anomalies)
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = f"""SHIFT REPORT
Generated: {report_time}
Period: Last 8 Hours

SUMMARY
Total Output: {total_output:,} units
Average Efficiency: {avg_efficiency}%
Total Downtime: {total_downtime} mins
Anomalies Detected: {anomaly_count}

LINE PERFORMANCE
"""
    for line in shift_df["Line"].unique():
        line_df = shift_df[shift_df["Line"] == line]
        line_output = line_df["Output"].sum()
        line_efficiency = round(line_df["Efficiency (%)"].mean(), 1)
        line_downtime = line_df["Downtime (mins)"].sum()
        line_anomalies = len(anomalies[anomalies["Line"] == line])
        report += f"""
{line}
  Output: {line_output:,} units
  Avg Efficiency: {line_efficiency}%
  Downtime: {line_downtime} mins
  Anomalies: {line_anomalies}
"""

    report += f"""
ATTENTION
Worst Performing Line: {worst_line} ({worst_efficiency}% avg efficiency)
Lines Below {efficiency_threshold}% Threshold: {shift_df[shift_df["Efficiency (%)"] < efficiency_threshold]["Line"].nunique()}
"""
    return report

# Split into time windows
now = datetime.now()
current_df = df[df["Time"] >= now - timedelta(hours=12)]
previous_df = df[df["Time"] < now - timedelta(hours=12)]
shift_df = df[df["Time"] >= now - timedelta(hours=8)]

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
zscore_sensitivity = st.sidebar.slider(
    "Anomaly Sensitivity (Z-Score)",
    min_value=1.0,
    max_value=3.0,
    value=2.0,
    step=0.1,
    help="Lower values catch more anomalies. Higher values only flag extreme ones."
)

filtered_df = df[df["Line"].isin(selected_lines)].copy()
filtered_current = current_df[current_df["Line"].isin(selected_lines)]
filtered_previous = previous_df[previous_df["Line"].isin(selected_lines)]
filtered_shift = shift_df[shift_df["Line"].isin(selected_lines)].copy()

# Run anomaly detection
filtered_df = detect_anomalies(filtered_df, "Output", threshold=zscore_sensitivity)
filtered_shift = detect_anomalies(filtered_shift, "Output", threshold=zscore_sensitivity)
anomalies_df = filtered_df[filtered_df["Anomaly"] == True]
shift_anomalies_df = filtered_shift[filtered_shift["Anomaly"] == True]

# KPI Cards
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

current_output = filtered_current["Output"].sum()
previous_output = filtered_previous["Output"].sum()
output_delta = current_output - previous_output

current_efficiency = round(filtered_current["Efficiency (%)"].mean(), 1)
previous_efficiency = round(filtered_previous["Efficiency (%)"].mean(), 1)
efficiency_delta = round(current_efficiency - previous_efficiency, 1)

current_downtime = filtered_current["Downtime (mins)"].sum()
previous_downtime = filtered_previous["Downtime (mins)"].sum()
downtime_delta = current_downtime - previous_downtime

total_anomalies = len(anomalies_df)

col1.metric("Total Output (Last 12hrs)", f"{current_output:,} units", delta=f"{output_delta:,} vs previous 12hrs")
col2.metric("Avg Efficiency (Last 12hrs)", f"{current_efficiency}%", delta=f"{efficiency_delta}% vs previous 12hrs")
col3.metric("Total Downtime (Last 12hrs)", f"{current_downtime} mins", delta=f"{downtime_delta} mins vs previous 12hrs", delta_color="inverse")
col4.metric("Anomalies Detected", f"{total_anomalies}", delta=None)

st.divider()

# Alerts Panel
st.subheader("Alerts")

low_efficiency = filtered_df[filtered_df["Efficiency (%)"] < efficiency_threshold]
alert_count = 0

if not low_efficiency.empty:
    alert_summary = low_efficiency.groupby("Line").size().reset_index(name="Incidents")
    for _, row in alert_summary.iterrows():
        st.warning(f"{row['Line']}: {row['Incidents']} readings below {efficiency_threshold}% efficiency threshold")
        alert_count += 1

if not anomalies_df.empty:
    anomaly_summary = anomalies_df.groupby("Line").size().reset_index(name="Anomalies")
    for _, row in anomaly_summary.iterrows():
        st.error(f"{row['Line']}: {row['Anomalies']} output anomalies detected (Z-Score > {zscore_sensitivity})")
        alert_count += 1

if alert_count == 0:
    st.success("All lines operating within normal parameters.")

st.divider()

# Charts
col5, col6 = st.columns(2)

with col5:
    st.subheader("Output Over Time")
    fig1 = go.Figure()
    for line in selected_lines:
        line_df = filtered_df[filtered_df["Line"] == line]
        normal_df = line_df[line_df["Anomaly"] == False]
        anomaly_line_df = line_df[line_df["Anomaly"] == True]
        fig1.add_trace(go.Scatter(
            x=normal_df["Time"], y=normal_df["Output"],
            mode="lines", name=line
        ))
        fig1.add_trace(go.Scatter(
            x=anomaly_line_df["Time"], y=anomaly_line_df["Output"],
            mode="markers", name=f"{line} Anomaly",
            marker=dict(color="red", size=10, symbol="x")
        ))
    st.plotly_chart(fig1, use_container_width=True)

with col6:
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

# Shift Report Section
st.divider()
st.subheader("Shift Report")
report_col1, report_col2, report_col3 = st.columns([2, 1, 1])

with report_col1:
    st.caption("Generate a summary report for the last 8 hours across selected lines.")

with report_col2:
    report_text = generate_shift_report(filtered_shift, shift_anomalies_df, efficiency_threshold)
    st.download_button(
        label="Download Report (.txt)",
        data=report_text,
        file_name=f"shift_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain"
    )

with report_col3:
    st.download_button(
        label="Download Raw Data (.csv)",
        data=filtered_shift.to_csv(index=False),
        file_name=f"shift_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

st.divider()

# Anomaly Log
if not anomalies_df.empty:
    st.subheader("Anomaly Log")
    st.dataframe(
        anomalies_df[["Time", "Line", "Output", "Z-Score"]].sort_values("Time", ascending=False).reset_index(drop=True),
        use_container_width=True
    )
    st.divider()

# Raw Data Table
st.subheader("Raw Readings")
st.dataframe(
    filtered_df.sort_values("Time", ascending=False).reset_index(drop=True),
    use_container_width=True
)