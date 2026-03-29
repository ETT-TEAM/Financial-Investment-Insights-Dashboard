# Financial Investment Insights Dashboard
### *Data Analysis + Visualization + AI-Based Insight Generation*

---

## Project Overview

This project is a comprehensive **Financial Investment Insights Dashboard** that combines interactive data analysis with AI-powered natural language insights. It analyses stock market data (AAPL, MSFT, GOOG) and a mutual fund portfolio (814 schemes) to deliver actionable financial intelligence through visualizations and human-readable explanations.

The project bridges the gap between raw financial data and actionable intelligence, making it accessible to users without deep financial expertise.

---

## Objectives

- **Data Collection & Cleaning**: Load and standardize raw financial datasets
- **Exploratory Data Analysis**: Generate 8+ publication-quality visualizations
- **Financial Metrics**: Compute returns, volatility, and risk-adjusted performance
- **AI-Powered Insights**: Generate LLM-style natural language financial insights
- **Interactive Dashboard**: Deliver findings through a Streamlit web application
- **Power BI Integration**: Export dashboard-ready data for enterprise reporting

---

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Core programming language |
| **Pandas / NumPy** | Data manipulation and analysis |
| **Matplotlib / Seaborn** | Static visualizations (notebooks) |
| **Plotly** | Interactive charts (dashboard) |
| **Streamlit** | Web-based dashboard application |
| **Jupyter Notebook** | Interactive analysis environment |
| **Power BI** | Enterprise dashboard (optional) |

---

## Project Structure

```
Financial-Investment-Insights-Dashboard/
│
├── data/
│ ├── raw/       # Original datasets
│ │ ├── AAPL_raw.csv    # Apple stock data
│ │ ├── MSFT_raw.csv    # Microsoft stock data
│ │ ├── GOOG_raw.csv    # Google stock data
│ │ └── comprehensive_mutual_funds_data.csv
│ └── processed/     # Cleaned & export-ready data
│  ├── all_stocks_clean.csv
│  ├── mutual_funds_clean.csv
│  ├── stock_summary.csv
│  ├── mf_category_summary.csv
│  └── ai_insights.csv
│
├── notebooks/
│ ├── 01_data_collection.ipynb  # Data loading & overview
│ ├── 02_data_cleaning.ipynb  # Cleaning & preprocessing
│ ├── 03_eda_analysis.ipynb   # Exploratory data analysis
│ └── 04_llm_insights.ipynb  # AI insight generation
│
├── src/
│ ├── __init__.py
│ ├── data_processing.py   # Data loading & cleaning pipeline
│ ├── metrics.py     # Financial metrics computation
│ └── insight_engine.py   # LLM-inspired insight generator
│
├── dashboard/
│ ├── app.py      # Streamlit dashboard application
│ ├── financial_dashboard.pbix  # Power BI file
│ └── README.md     # Dashboard setup instructions
│
├── requirements.txt
└── README.md      # This file
```

---

## Workflow

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ 1. Data   │ ─── │ 2. Data   │ ─── │ 3. Exploratory │
│ Collection  │  │ Cleaning   │  │ Data Analysis │
│ (01_notebook) │  │ (02_notebook) │  │ (03_notebook) │
└──────────────────┘  └──────────────────┘  └──────────────────┘
                │
┌──────────────────┐  ┌──────────────────┐    │
│ 5. Dashboard  │ ── │ 4. AI Insight │ ────────────┘
│ (Streamlit/PBI) │  │ Generation  │
│     │  │ (04_notebook) │
└──────────────────┘  └──────────────────┘
```

---

## How to Run the Project

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run Data Processing Pipeline

```bash
python src/data_processing.py
```

This cleans all raw data and generates processed CSVs.

### Step 3: Run Notebooks (Optional)

```bash
jupyter notebook notebooks/
```

Open and run notebooks 01 through 04 in order.

### Step 4: Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

Open your browser to `http://localhost:8501` to explore the interactive dashboard.

---

## Sample Outputs

### Stock Price Trends
Line chart showing AAPL, MSFT, and GOOG closing prices over the analysis period with distinct color coding.

### Risk vs Return Scatter
Interactive scatter plot positioning each stock by volatility (x-axis) and average daily return (y-axis), with bubble size indicating cumulative return.

### AI-Generated Insights (Sample)
> *"Microsoft shows the highest average daily return of 0.07%, accompanied by higher volatility (σ = 1.95%). This suggests strong upward momentum but investors should be mindful of the associated risk."*

> *"The risk-return tradeoff shows a moderate positive correlation (r = 0.45). Higher-risk investments tend to yield higher returns. MSFT offers the best risk-adjusted return (Sharpe proxy = 0.036)."*

> *"Among mutual fund categories, 'Equity' leads with an average 1-year return of 12.3%. 'Debt' offers the lowest average risk, making it suitable for conservative investors."*

### Dashboard Features
- **3 Interactive Tabs**: Stock Analysis, Mutual Funds, AI Insights
- **Dynamic Filters**: Stock ticker, date range, MF category, risk level
- **9 AI Insight Cards**: Downloadable as a text report
- **Responsive Charts**: Powered by Plotly with hover details

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Data Cleaning** | Standardized columns, removed `$` symbols, parsed dates, filled missing values |
| **8+ Visualizations** | Price trends, normalized comparison, return distributions, volatility, risk-return scatter, category distribution, top funds, correlation heatmap |
| **Financial Metrics** | Average return, volatility (σ), Sharpe ratio proxy, cumulative return |
| **AI Insight Engine** | 9 rule-based insights mimicking LLM output with context-aware analysis |
| **Interactive Dashboard** | Streamlit app with filters, tabs, and downloadable reports |
| **Power BI Ready** | CSV exports compatible with Power BI / Tableau import |

---

## Insight Engine Architecture

The `InsightEngine` class in `src/insight_engine.py` generates human-readable insights using deterministic rules structured to mimic LLM output:

- **Market Overview** — Overall sentiment and average performance
- **Highest Return Stock** — Best performer with volatility context
- **Lowest Risk Stock** — Most stable investment option
- **Risk-Return Tradeoff** — Correlation analysis with Sharpe ratio
- **Cumulative Performance** — Long-term investment growth comparison
- **Top MF Performers** — Highest-return mutual funds
- **Category Analysis** — Best and safest MF categories
- **MF Risk-Return** — Mutual fund risk-return correlation
- **Long-term Consistency** — 1yr/3yr/5yr return trend analysis

---

## Datasets

### Stock Data
| Field | Description |
|-------|-------------|
| Date | Trading date |
| Close/Last | Closing price (with `$` symbol) |
| Volume | Trading volume |
| Open, High, Low | OHLC prices |

### Mutual Funds Data
| Field | Description |
|-------|-------------|
| scheme_name | Fund name |
| category / sub_category | Fund classification |
| returns_1yr / 3yr / 5yr | Historical returns |
| sd | Standard deviation (risk) |
| sharpe, sortino, alpha, beta | Risk-adjusted metrics |
| risk_level | Risk classification |
| rating | Fund rating |

---

## License

This project is for academic and educational purposes.

---

*Built with using Python, Streamlit, and AI-powered insights*
