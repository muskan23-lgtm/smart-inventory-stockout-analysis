from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def build_inventory_analysis(target_coverage_days: int = 14) -> pd.DataFrame:
    products = pd.read_csv(DATA / "products.csv")
    sales = pd.read_csv(DATA / "daily_sales.csv", parse_dates=["date"])
    inventory = pd.read_csv(DATA / "inventory.csv")

    if sales.empty or products.empty or inventory.empty:
        raise ValueError("Input data files must not be empty.")
    if (sales["quantity_sold"] < 0).any():
        raise ValueError("quantity_sold cannot be negative.")
    if products["product_id"].duplicated().any():
        raise ValueError("products.csv contains duplicate product_id values.")

    days = max(1, sales["date"].nunique())
    sales_summary = (
        sales.groupby("product_id", as_index=False)
        .agg(total_units_sold=("quantity_sold", "sum"),
             active_sales_days=("date", "nunique"))
    )
    sales_summary["avg_daily_demand"] = sales_summary["total_units_sold"] / days

    result = products.merge(sales_summary, on="product_id", how="left")
    result = result.merge(inventory, on="product_id", how="left")
    result["avg_daily_demand"] = result["avg_daily_demand"].fillna(0)
    result["current_stock"] = result["current_stock"].fillna(0)
    result["reorder_lead_time_days"] = result["reorder_lead_time_days"].fillna(0)

    result["estimated_days_of_stock"] = np.where(
        result["avg_daily_demand"] > 0,
        result["current_stock"] / result["avg_daily_demand"],
        np.inf
    )
    result["lead_time_demand"] = result["avg_daily_demand"] * result["reorder_lead_time_days"]
    result["safety_stock"] = np.ceil(0.20 * result["lead_time_demand"])
    result["reorder_point"] = np.ceil(result["lead_time_demand"] + result["safety_stock"])
    result["suggested_reorder_qty"] = np.maximum(
        0, np.ceil(result["avg_daily_demand"] * target_coverage_days - result["current_stock"])
    ).astype(int)
    result["daily_revenue"] = result["total_units_sold"] * result["unit_price"] / days
    result["gross_margin_pct"] = (
        (result["unit_price"] - result["unit_cost"]) / result["unit_price"] * 100
    ).round(1)

    def classify(row):
        if row["avg_daily_demand"] <= 0:
            return "No recent demand"
        if row["current_stock"] <= row["reorder_point"]:
            return "High stockout risk"
        if row["estimated_days_of_stock"] > 45:
            return "Potential overstock"
        return "Healthy"

    result["stock_status"] = result.apply(classify, axis=1)
    return result.sort_values(["stock_status", "suggested_reorder_qty"], ascending=[True, False])

if __name__ == "__main__":
    result = build_inventory_analysis()
    output = ROOT / "data" / "inventory_recommendations.csv"
    result.to_csv(output, index=False)
    print(f"Analysis complete. Saved: {output}")
    cols = ["product_name", "category", "current_stock", "avg_daily_demand",
            "estimated_days_of_stock", "reorder_point", "suggested_reorder_qty", "stock_status"]
    print(result[cols].round(2).to_string(index=False))
