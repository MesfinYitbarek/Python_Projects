import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Dashboard Title
# ---------------------------
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📈 Sales Performance Dashboard")

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    # Sample dataset – you can replace this with your own CSV file
    data = pd.DataFrame({
        "Region": ["North", "South", "East", "West"] * 5,
        "Sales": [200, 150, 300, 250, 220, 170, 310, 270, 210, 160, 320, 280, 230, 180, 330, 290, 240, 190, 340, 300],
        "Month": ["Jan", "Feb", "Mar", "Apr", "May"] * 4
    })
    return data

data = load_data()

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("🔍 Filter Options")
regions = st.sidebar.multiselect("Select Regions", options=data["Region"].unique(), default=data["Region"].unique())
months = st.sidebar.multiselect("Select Months", options=data["Month"].unique(), default=data["Month"].unique())

filtered_data = data.query("Region in @regions and Month in @months")

# ---------------------------
# KPI Metrics
# ---------------------------
total_sales = filtered_data["Sales"].sum()
avg_sales = filtered_data["Sales"].mean()
num_records = len(filtered_data)

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📊 Average Sale", f"${avg_sales:,.0f}")
col3.metric("🧾 Records", num_records)

# ---------------------------
# Charts
# ---------------------------
st.subheader("📉 Sales by Region")
region_sales = filtered_data.groupby("Region")["Sales"].sum()
fig, ax = plt.subplots()
region_sales.plot(kind="bar", ax=ax, color="skyblue")
st.pyplot(fig)

st.subheader("📆 Sales by Month")
month_sales = filtered_data.groupby("Month")["Sales"].sum().reindex(["Jan", "Feb", "Mar", "Apr", "May"])
fig2, ax2 = plt.subplots()
month_sales.plot(kind="line", ax=ax2, marker="o", color="green")
st.pyplot(fig2)

# ---------------------------
# Display Data
# ---------------------------
st.subheader("🗂️ Filtered Data")
st.dataframe(filtered_data)
