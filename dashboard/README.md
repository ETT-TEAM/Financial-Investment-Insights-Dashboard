# Power BI Dashboard Setup Instructions

## Overview
This directory contains materials for the Financial Investment Insights Dashboard. 
The dashboard can be built using either **Power BI** (provided `.pbix` file) or 
the included **Streamlit app** (`app.py`).

---

## Option 1: Power BI Dashboard

### Pre-built File
- `financial_dashboard.pbix` — Power BI Desktop file (if available)

### Setting Up from Scratch

#### Step 1: Import Data
Import the following CSV files from `data/processed/`:

| File | Description |
|------|-------------|
| `all_stocks_clean.csv` | Cleaned stock data (AAPL, MSFT, GOOG) |
| `mutual_funds_clean.csv` | Cleaned mutual fund data (814 schemes) |
| `stock_summary.csv` | Aggregated stock metrics |
| `mf_category_summary.csv` | Mutual fund category summary |
| `ai_insights.csv` | AI-generated insights text |

#### Step 2: Create Visualizations

1. **Stock Price Trend Chart**
 - Chart Type: Line Chart
 - X-axis: `date`
 - Y-axis: `close`
 - Legend: `ticker`
 - Filter: Date slicer

2. **Risk vs Return (Stocks)**
 - Chart Type: Scatter Plot
 - X-axis: `volatility` (from stock_summary)
 - Y-axis: `avg_daily_return`
 - Labels: `ticker`

3. **Mutual Fund Category Distribution**
 - Chart Type: Horizontal Bar Chart
 - Axis: `category`
 - Values: Count of `scheme_name`

4. **Mutual Fund Risk vs Return**
 - Chart Type: Scatter Plot
 - X-axis: `sd` (standard deviation)
 - Y-axis: `returns_1yr`
 - Color: `risk_level`

5. **AI Insights Text Panel**
 - Add a Multi-row Card or Text Box
 - Data source: `ai_insights.csv`
 - Display: `insight` column

#### Step 3: Add Filters
- **Date Slicer** for stock data
- **Stock Ticker Slicer** (AAPL, MSFT, GOOG)
- **Category Slicer** for mutual funds
- **Risk Level Slicer**

---

## Option 2: Streamlit Dashboard (Recommended)

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard/app.py
```

### Features
- **Stock Analysis Tab**: Price trends, normalized comparison, return distributions, risk-return scatter
- **Mutual Funds Tab**: Category distribution, risk-return analysis, top performers
- **AI Insights Tab**: LLM-inspired financial intelligence with downloadable report
- **Interactive Filters**: Stock selection, date range, MF categories, risk levels

### Dashboard Sections
| Section | Visualizations |
|---------|---------------|
| Key Metrics | Stocks analysed, avg return, avg volatility, fund count |
| Stock Analysis | Line chart, normalized chart, histograms, scatter plot, bar chart |
| Mutual Funds | Category bar chart, risk-return scatter, top funds table |
| AI Insights | 9 insight cards with download option |

---

## Data Pipeline
Before using either dashboard, run the data processing pipeline:

```bash
cd <project_root>
python src/data_processing.py
```

This generates all required CSV files in `data/processed/`.
