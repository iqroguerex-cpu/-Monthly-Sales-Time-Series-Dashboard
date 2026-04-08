import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monthly Sales Dashboard", layout="wide")

st.title("📈 Monthly Sales Time-Series Dashboard")

# -------------------------------
# Load default dataset from repo
# -------------------------------
@st.cache_data
def load_default_data():
    return pd.read_csv("monthly_sales.csv", parse_dates=["date"], encoding="utf-8-sig")

# File uploader (optional override)
file = st.file_uploader("Upload monthly_sales.csv (optional)", type=["csv"])

if file is not None:
    df = pd.read_csv(file, parse_dates=["date"], encoding="utf-8-sig")
else:
    try:
        df = load_default_data()
        st.success("Loaded dataset from repository ✅")
    except FileNotFoundError:
        st.error("monthly_sales.csv not found in repo. Please upload a file.")
        st.stop()

# -------------------------------
# Clean columns
# -------------------------------
df.columns = df.columns.str.strip().str.lower()

# -------------------------------
# Feature Engineering
# -------------------------------
df["revenue"] = df["units_sold"] * df["unit_price"]
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

# -------------------------------
# Sidebar Filter
# -------------------------------
stores = df["store"].unique()
selected_store = st.sidebar.selectbox(
    "Select Store (or All)",
    ["All"] + list(stores)
)

if selected_store != "All":
    df = df[df["store"] == selected_store]

# -------------------------------
# Aggregations
# -------------------------------
monthly_total = (
    df.groupby("month")["revenue"]
    .sum()
    .sort_index()
)

cumulative = monthly_total.cumsum()
rolling_avg = monthly_total.rolling(window=2).mean()

# -------------------------------
# KPIs
# -------------------------------
st.subheader("📌 Key Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"${monthly_total.sum():,.0f}")
col2.metric("Best Month Revenue", f"${monthly_total.max():,.0f}")
col3.metric("Latest Month Revenue", f"${monthly_total.iloc[-1]:,.0f}")

st.divider()

# -------------------------------
# Charts
# -------------------------------
st.subheader("📈 Monthly Revenue")
st.line_chart(monthly_total)

st.subheader("📈 Cumulative Revenue")
st.line_chart(cumulative)

st.subheader("📉 2-Month Rolling Average Revenue")
st.line_chart(rolling_avg)

# -------------------------------
# Store Comparison
# -------------------------------
if selected_store == "All":
    st.subheader("🏪 Store Comparison")

    store_monthly = (
        df.groupby(["store", "month"])["revenue"]
        .sum()
        .reset_index()
    )

    pivot = store_monthly.pivot(
        index="month",
        columns="store",
        values="revenue"
    )

    st.line_chart(pivot)
