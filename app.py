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

# Sidebar Filters
st.sidebar.header("Filters")
selected_lines = st.sidebar.multiselect("Select Lines", ["Line A", "Line B", "Line C"], default=["Line A", "Line B", "Line C"])
filtered_df = df[df["Line"].isin(selected_lines)]

# KPI Cards
st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3)
col1.metric("Total Output", f"{filtered_df['Output'].sum():,} units")
col2.metric("Avg Efficiency", f"{filtered_df['Efficiency (%)'].mean():.1f}%")
col3.metric("Total Downtime", f"{filtered_df['Downtime (mins)'].sum()} mins")

st.divider()

# Charts
col4, col5 = st.columns(2)

with col4:
    st.subheader("Output Over Time")
    fig1 = px.line(filtered_df, x="Time", y="Output", color="Line")
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.subheader("Downtime by Line")
    fig2 = px.bar(filtered_df.groupby("Line")["Downtime (mins)"].sum().reset_index(), x="Line", y="Downtime (mins)", color="Line")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Efficiency Over Time")
fig3 = px.line(filtered_df, x="Time", y="Efficiency (%)", color="Line")
st.plotly_chart(fig3, use_container_width=True)