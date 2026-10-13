# Smart Inventory & Stockout Analysis

A beginner-friendly data analytics portfolio project designed to help a retailer identify fast-moving products, stockout risks, and potential overstocking.

## Business problem
Retailers can lose sales when popular products run out of stock and tie up cash when slow-moving products are overstocked. This project combines product, daily sales, and inventory data to produce practical replenishment recommendations.

## Features
- Product/category sales and revenue analysis
- Average daily demand and estimated days of inventory remaining
- Reorder point based on average demand and supplier lead time
- Simple reorder quantity recommendation
- Stockout-risk and overstock flags
- Streamlit dashboard with filters and charts
- SQL examples for common analyst questions
- Synthetic sample data included

## Tools
Python, Pandas, NumPy, Plotly, Streamlit, SQL.

## Project structure
```text
smart_inventory_stockout_analysis/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── products.csv
│   ├── daily_sales.csv
│   └── inventory.csv
├── src/
│   └── analyze_inventory.py
├── sql/
│   └── queries.sql
└── reports/
    └── interview_notes.md
```

## Run on Windows (VS Code)
1. Extract the ZIP file.
2. Open the extracted folder in VS Code.
3. Open Terminal → New Terminal.
4. Create and activate a virtual environment (optional but recommended):
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
5. Install packages:
   ```powershell
   pip install -r requirements.txt
   ```
6. Run the analysis:
   ```powershell
   python src/analyze_inventory.py
   ```
7. Launch the dashboard:
   ```powershell
   streamlit run app.py
   ```
8. Streamlit will print a local URL (usually http://localhost:8501). Open it in your browser.

## How calculations work
- Average daily demand = total quantity sold / number of calendar days in the dataset.
- Lead-time demand = average daily demand × supplier lead time.
- Safety stock = 20% of lead-time demand (a simple demonstration assumption).
- Reorder point = lead-time demand + safety stock.
- Suggested reorder quantity = max(0, (average daily demand × target coverage days) − current stock).
- Days of stock remaining = current stock / average daily demand.

These are starter heuristics, not a production-grade forecasting system. For a real business, validate seasonality, demand variability, supplier reliability, pack sizes, budget limits, and service-level targets before ordering.

## Data notes
All data is synthetic and created for learning. It does not represent any real company. Inventory is a single snapshot; sales are daily synthetic records for 2025.

## What to explain in an interview
"I built a small inventory analytics system using Python, SQL, and a Streamlit dashboard. It analyzes daily sales and current inventory to identify products that may run out of stock, estimates reorder points using supplier lead times, and suggests reorder quantities. The dashboard helps a business prioritize which products need attention. I used synthetic data, so the results demonstrate the workflow rather than real-world savings."

## Suggested next improvements
- Add a demand forecast model and compare it against a naive baseline.
- Add purchase orders and supplier delivery history.
- Connect the data to SQLite/PostgreSQL and run the SQL queries.
- Add tests for zero demand, missing values, and unusual stock levels.
- Export recommendations to CSV for review.
