"""
 Financial Investment Insights Dashboard
============================================
Interactive Streamlit dashboard combining stock analysis,
mutual fund insights, and AI-generated financial intelligence.

Run: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from data_processing import load_and_clean_all_stocks, load_raw_mutual_funds, clean_mutual_funds
from metrics import compute_stock_metrics, risk_return_comparison, compute_mf_metrics, top_mutual_funds, mf_risk_return_analysis
from insight_engine import InsightEngine

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
 page_title="Financial Investment Insights Dashboard",
 page_icon="",
 layout="wide",
 initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    /* Professional Dark Theme CSS */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 95%; }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 600; color: #f8fafc; }
    [data-testid="stMetricLabel"] { font-size: 0.9rem; font-weight: 500; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; }
    [data-testid="metric-container"] { 
        background-color: #1e293b; 
        border: 1px solid #334155; 
        border-radius: 8px; 
        padding: 1.25rem; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Headers */
    h1, h2, h3 { color: #f8fafc !important; font-weight: 600 !important; letter-spacing: -0.025em; }
    hr { border-color: #334155; margin-top: 2rem; margin-bottom: 2rem; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { border-right: 1px solid #334155; background-color: #0f172a; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #334155; }
    .stTabs [data-baseweb="tab"] { 
        padding: 10px 20px; 
        background-color: transparent; 
        border-radius: 6px 6px 0 0; 
        color: #cbd5e1; 
        font-weight: 500; 
    }
    .stTabs [aria-selected="true"] { color: #3b82f6 !important; border-bottom-color: #3b82f6 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DATA LOADING (cached)
# ══════════════════════════════════════════════════════════════
RAW_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
TICKERS = ['AAPL', 'MSFT', 'GOOG']

@st.cache_data
def load_data():
 stocks = load_and_clean_all_stocks(TICKERS, RAW_DIR)
 mf = clean_mutual_funds(load_raw_mutual_funds(RAW_DIR))
 stock_metrics = compute_stock_metrics(stocks)
 return stocks, mf, stock_metrics

stocks, mf, stock_metrics = load_data()

# ══════════════════════════════════════════════════════════════
# SIDEBAR — Filters
# ══════════════════════════════════════════════════════════════
st.sidebar.title(" Filters")

# Stock filters
st.sidebar.subheader("Stock Filters")
selected_tickers = st.sidebar.multiselect(
 "Select Stocks", TICKERS, default=TICKERS
)

date_range = st.sidebar.date_input(
 "Date Range",
 value=[stocks['date'].min(), stocks['date'].max()],
 min_value=stocks['date'].min(),
 max_value=stocks['date'].max(),
)

# Mutual fund filters
st.sidebar.subheader("Mutual Fund Filters")
categories = sorted(mf['category'].unique())
selected_categories = st.sidebar.multiselect(
 "Select Categories", categories, default=categories[:5]
)

risk_levels = sorted(mf['risk_level'].unique())
selected_risk = st.sidebar.multiselect(
 "Risk Level", risk_levels, default=risk_levels
)

# Apply filters
filtered_stocks = stocks[
 (stocks['ticker'].isin(selected_tickers)) &
 (stocks['date'] >= pd.Timestamp(date_range[0])) &
 (stocks['date'] <= pd.Timestamp(date_range[1]))
]

filtered_mf = mf[
 (mf['category'].isin(selected_categories)) &
 (mf['risk_level'].isin(selected_risk))
]

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.title(" Financial Investment Insights Dashboard")
st.markdown("*Combining Data Analysis with AI-Powered Financial Intelligence*")
st.markdown("---")

# ══════════════════════════════════════════════════════════════
# KEY METRICS ROW
# ══════════════════════════════════════════════════════════════
m1, m2, m3, m4 = st.columns(4)

with m1:
 st.metric(" Stocks Analysed", len(selected_tickers))
with m2:
 avg_ret = stock_metrics[stock_metrics['ticker'].isin(selected_tickers)]['avg_daily_return'].mean()
 st.metric(" Avg Daily Return", f"{avg_ret:.4f}%")
with m3:
 avg_vol = stock_metrics[stock_metrics['ticker'].isin(selected_tickers)]['volatility'].mean()
 st.metric(" Avg Volatility", f"{avg_vol:.4f}%")
with m4:
 st.metric(" Mutual Funds", len(filtered_mf))

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# TAB LAYOUT
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([" Stock Analysis", " Mutual Funds", " AI Insights"])

# ── TAB 1: Stock Analysis ─────────────────────────────────────
with tab1:
 col1, col2 = st.columns(2)

 with col1:
  st.subheader(" Stock Price Trends")
  fig = px.line(
   filtered_stocks, x='date', y='close', color='ticker',
   title='Stock Closing Prices Over Time',
   labels={'close': 'Close Price ($)', 'date': 'Date'},
   template='plotly_dark',
  )
  fig.update_layout(
   height=400,
   legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
  )
  st.plotly_chart(fig, use_container_width=True)

 with col2:
  st.subheader(" Normalized Price Comparison")
  norm_data = []
  for ticker in selected_tickers:
   subset = filtered_stocks[filtered_stocks['ticker'] == ticker].copy()
   if len(subset) > 0:
    first_price = subset['close'].iloc[0]
    subset['normalized'] = (subset['close'] / first_price) * 100
    norm_data.append(subset)

  if norm_data:
   norm_df = pd.concat(norm_data)
   fig = px.line(
    norm_df, x='date', y='normalized', color='ticker',
    title='Normalized Prices (Base = 100)',
    labels={'normalized': 'Normalized Price', 'date': 'Date'},
    template='plotly_dark',
   )
   fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)
   fig.update_layout(height=400)
   st.plotly_chart(fig, use_container_width=True)

 # Row 2
 col3, col4 = st.columns(2)

 with col3:
  st.subheader(" Daily Return Distribution")
  fig = go.Figure()
  for ticker in selected_tickers:
   returns = filtered_stocks[filtered_stocks['ticker'] == ticker]['daily_return'].dropna()
   fig.add_trace(go.Histogram(
    x=returns, name=ticker, opacity=0.7, nbinsx=60
   ))
  fig.update_layout(
   barmode='overlay', title='Daily Return Distributions',
   xaxis_title='Daily Return (%)', yaxis_title='Frequency',
   template='plotly_dark', height=400,
  )
  st.plotly_chart(fig, use_container_width=True)

 with col4:
  st.subheader(" Risk vs Return")
  filtered_metrics = stock_metrics[stock_metrics['ticker'].isin(selected_tickers)]
  fig = px.scatter(
   filtered_metrics, x='volatility', y='avg_daily_return',
   text='ticker', size='cumulative_return_pct',
   title='Risk vs Return — Stocks',
   labels={'volatility': 'Volatility (σ %)', 'avg_daily_return': 'Avg Daily Return (%)'},
   template='plotly_dark',
   size_max=40,
  )
  fig.update_traces(textposition='top center', textfont_size=14)
  fig.update_layout(height=400)
  st.plotly_chart(fig, use_container_width=True)

 # Volatility bar chart
 st.subheader(" Volatility Comparison")
 fig = px.bar(
  filtered_metrics, x='ticker', y='volatility',
  color='ticker', title='Volatility (Standard Deviation of Daily Returns)',
  labels={'volatility': 'Volatility (σ %)', 'ticker': 'Stock'},
  template='plotly_dark', text='volatility',
 )
 fig.update_traces(texttemplate='%{text:.4f}%', textposition='outside')
 fig.update_layout(height=350, showlegend=False)
 st.plotly_chart(fig, use_container_width=True)

 # Metrics table
 st.subheader(" Stock Metrics Summary")
 st.dataframe(filtered_metrics.style.format({
  'avg_daily_return': '{:.4f}%',
  'volatility': '{:.4f}%',
  'sharpe_proxy': '{:.4f}',
  'cumulative_return_pct': '{:.2f}%',
  'avg_close': '${:.2f}',
 }), use_container_width=True)


# ── TAB 2: Mutual Funds ──────────────────────────────────────
with tab2:
 col1, col2 = st.columns(2)

 with col1:
  st.subheader(" Category Distribution")
  cat_counts = filtered_mf['category'].value_counts().reset_index()
  cat_counts.columns = ['category', 'count']
  fig = px.bar(
   cat_counts.head(15), x='count', y='category',
   orientation='h', title='Funds per Category',
   labels={'count': 'Number of Funds', 'category': 'Category'},
   template='plotly_dark', color='count',
   color_continuous_scale='viridis',
  )
  fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
  st.plotly_chart(fig, use_container_width=True)

 with col2:
  st.subheader(" Risk vs Return")
  fig = px.scatter(
   filtered_mf, x='sd', y='returns_1yr', color='risk_level',
   hover_data=['scheme_name', 'category'],
   title='Mutual Fund Risk vs 1-Year Return',
   labels={'sd': 'Risk (Std Dev)', 'returns_1yr': '1-Year Return (%)'},
   template='plotly_dark', opacity=0.7,
  )
  # Trend line
  valid = filtered_mf[['sd', 'returns_1yr']].dropna()
  if len(valid) > 2:
   z = np.polyfit(valid['sd'], valid['returns_1yr'], 1)
   p = np.poly1d(z)
   x_line = np.linspace(valid['sd'].min(), valid['sd'].max(), 100)
   fig.add_trace(go.Scatter(
    x=x_line, y=p(x_line), mode='lines',
    name='Trend', line=dict(dash='dash', color='red', width=2)
   ))
  fig.update_layout(height=500)
  st.plotly_chart(fig, use_container_width=True)

 # Top funds table
 top_n = st.slider("Number of top funds to display", 5, 30, 10)
 st.subheader(f" Top {top_n} Mutual Funds by 1-Year Return")
 top = top_mutual_funds(filtered_mf, 'returns_1yr', top_n)
 st.dataframe(
  top.style.format({
   'returns_1yr': '{:.1f}%',
   'returns_3yr': '{:.1f}%',
   'returns_5yr': '{:.1f}%',
   'sd': '{:.2f}',
  }),
  use_container_width=True,
 )

 # Category metrics
 st.subheader(" Category-wise Performance")
 cat_metrics = compute_mf_metrics(filtered_mf)
 fig = px.scatter(
  cat_metrics, x='avg_risk', y='avg_return_1yr',
  size='count', text='category',
  title='Category Risk vs Average Return',
  labels={'avg_risk': 'Avg Risk (σ)', 'avg_return_1yr': 'Avg 1-Year Return (%)'},
  template='plotly_dark', size_max=50,
 )
 fig.update_traces(textposition='top center', textfont_size=10)
 fig.update_layout(height=500)
 st.plotly_chart(fig, use_container_width=True)


# ── TAB 3: AI Insights ───────────────────────────────────────
with tab3:
 st.subheader(" AI-Generated Financial Insights")
 st.markdown("*Powered by our rule-based LLM-inspired Insight Engine*")
 st.markdown("---")

 # Generate insights
 engine = InsightEngine(stock_metrics, mf, stocks)
 insights = engine.generate_dict()

 # Display in styled cards
 for key, value in insights.items():
  title = key.replace('_', ' ').title()
  st.markdown(f"""
  <div style="background-color: #1e293b; border: 1px solid #334155;
              border-radius: 8px; padding: 1.5rem; margin: 1rem 0;
              box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);">
   <h4 style="color: #3b82f6; margin: 0 0 0.75rem 0; font-weight: 600; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.05em;">{title}</h4>
   <p style="color: #e2e8f0; margin: 0; line-height: 1.6; font-size: 1rem;">{value}</p>
  </div>
  """, unsafe_allow_html=True)

 st.markdown("---")

 # Export button
 report = engine.generate_report()
 st.download_button(
  label=" Download Full Insights Report",
  data=report,
  file_name="financial_insights_report.txt",
  mime="text/plain",
 )

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
 "<div style='text-align:center; color:#666; padding:1rem;'>"
 " Financial Investment Insights Dashboard | "
 "Data Analysis + AI-Powered Insights | "
 "Built with Streamlit & Plotly"
 "</div>",
 unsafe_allow_html=True,
)
