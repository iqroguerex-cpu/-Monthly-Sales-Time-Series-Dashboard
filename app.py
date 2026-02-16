import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monthly Sales Dashboard", layout="wide")

st.title("📈 Monthly Sales Time-Series Dashboard")

file = st.file_uploader("Upload monthly_sales.csv", type=["csv"])

if file is not None:
    # Load data
    df = pd.read_csv(file, parse_dates=["date"], encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    # Revenue column
    df["revenue"] = df["units_sold"] * df["unit_price"]

    # Month column
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    # Sidebar filter
    stores = df["store"].unique()
    selected_store = st.sidebar.selectbox(
        "Select Store (or All)",
        ["All"] + list(stores)
    )

    if selected_store != "All":
        df = df[df["store"] == selected_store]

    # --- Monthly Aggregation ---
    monthly_total = (
        df.groupby("month")["revenue"]
        .sum()
        .sort_index()
    )

    cumulative = monthly_total.cumsum()
    rolling_avg = monthly_total.rolling(window=2).mean()

    # --- KPIs ---
    st.subheader("📌 Key Metrics")
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Revenue", f"${monthly_total.sum():,.0f}")
    col2.metric("Best Month Revenue", f"${monthly_total.max():,.0f}")
    col3.metric("Latest Month Revenue", f"${monthly_total.iloc[-1]:,.0f}")

    st.divider()

    # --- Charts ---
    st.subheader("📈 Monthly Revenue")
    st.line_chart(monthly_total)

    st.subheader("📈 Cumulative Revenue")
    st.line_chart(cumulative)

    st.subheader("📉 2-Month Rolling Average Revenue")
    st.line_chart(rolling_avg)

    # --- Store Comparison ---
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

else:
    st.info("Please upload monthly_sales.csv to begin.")
