from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from analyze_inventory import build_inventory_analysis

st.set_page_config(page_title="Smart Inventory Analytics", page_icon="📦", layout="wide")
st.title("📦 Smart Inventory & Stockout Analysis")
st.caption("Synthetic retail data | Inventory monitoring, reorder recommendations, and sales insights")

with st.sidebar:
    st.header("Dashboard filters")
    target_days = st.slider("Target stock coverage (days)", min_value=7, max_value=45, value=14, step=1)
    st.caption("This changes the suggested reorder quantity calculation.")
    category_choice = st.selectbox("Category", ["All"] + sorted(pd.read_csv(ROOT / "data/products.csv")["category"].unique().tolist()))

df = build_inventory_analysis(target_coverage_days=target_days)
if category_choice != "All":
    df = df[df["category"] == category_choice].copy()

total_units = int(df["total_units_sold"].sum())
total_revenue = float((df["total_units_sold"] * df["unit_price"]).sum())
risk_count = int((df["stock_status"] == "High stockout risk").sum())
reorder_units = int(df["suggested_reorder_qty"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Units sold in period", f"{total_units:,}")
c2.metric("Sales value (synthetic)", f"₹{total_revenue:,.0f}")
c3.metric("Products at stockout risk", risk_count)
c4.metric("Suggested reorder units", f"{reorder_units:,}")

st.subheader("Inventory status")
status_counts = df["stock_status"].value_counts().rename_axis("Status").reset_index(name="Products")
left, right = st.columns(2)
with left:
    fig = px.bar(status_counts, x="Status", y="Products", title="Products by stock status", text="Products")
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.bar(df.sort_values("total_units_sold", ascending=False), x="product_name", y="total_units_sold",
                 color="category", title="Total units sold by product")
    fig.update_layout(xaxis_title="", yaxis_title="Units sold")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Reorder recommendations")
show_cols = ["product_name", "category", "current_stock", "total_units_sold", "avg_daily_demand",
             "estimated_days_of_stock", "reorder_point", "suggested_reorder_qty", "stock_status"]
table = df[show_cols].copy()
table["avg_daily_demand"] = table["avg_daily_demand"].round(2)
table["estimated_days_of_stock"] = table["estimated_days_of_stock"].replace(float("inf"), None).round(1)
st.dataframe(table, use_container_width=True, hide_index=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered recommendations (CSV)", data=csv,
                   file_name="inventory_recommendations.csv", mime="text/csv")

st.info("These recommendations use simple heuristic rules and synthetic data. Validate demand, seasonality, supplier reliability, and business constraints before making real purchase decisions.")
