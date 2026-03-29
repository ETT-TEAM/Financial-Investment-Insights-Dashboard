"""
data_processing.py — Data Loading, Cleaning & Transformation
=============================================================
Standardizes raw stock (AAPL, MSFT, GOOG) and mutual fund CSV data
into analysis-ready DataFrames with consistent column naming,
proper types, and derived features (daily_return).
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
STOCK_TICKERS = ['AAPL', 'MSFT', 'GOOG']

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
 """Lowercase column names, strip whitespace, replace spaces/slashes."""
 df.columns = (
  df.columns
  .str.strip()
  .str.lower()
  .str.replace(' ', '_', regex=False)
  .str.replace('/', '_', regex=False)
 )
 return df


def _remove_dollar_sign(series: pd.Series) -> pd.Series:
 """Strip '$' and convert to float."""
 return (
  series
  .astype(str)
  .str.replace('$', '', regex=False)
  .str.replace(',', '', regex=False)
  .str.strip()
  .apply(pd.to_numeric, errors='coerce')
 )

# ---------------------------------------------------------------------------
# Stock data
# ---------------------------------------------------------------------------

def load_raw_stock(ticker: str, raw_dir: str = RAW_DIR) -> pd.DataFrame:
 """Load a single raw stock CSV into a DataFrame."""
 path = os.path.join(raw_dir, f'{ticker}_raw.csv')
 if not os.path.exists(path):
  raise FileNotFoundError(f"Raw data file not found: {path}")
 return pd.read_csv(path)


def clean_stock(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
 """
 Clean a raw stock DataFrame:
  1. Standardize column names
  2. Remove '$' symbols and convert to numeric
  3. Parse dates
  4. Sort by date ascending
  5. Handle missing values
  6. Add daily_return column (% change of close price)
  7. Add ticker column
 """
 df = df.copy()
 df = _standardize_columns(df)

 # Rename 'close_last' → 'close' for readability
 if 'close_last' in df.columns:
  df.rename(columns={'close_last': 'close'}, inplace=True)

 # Convert price columns
 price_cols = [c for c in ['close', 'open', 'high', 'low'] if c in df.columns]
 for col in price_cols:
  df[col] = _remove_dollar_sign(df[col])

 # Convert volume to numeric
 if 'volume' in df.columns:
  df['volume'] = pd.to_numeric(
   df['volume'].astype(str).str.replace(',', '', regex=False),
   errors='coerce'
  )

 # Parse date
 if 'date' in df.columns:
  df['date'] = pd.to_datetime(df['date'], errors='coerce')

 # Sort ascending by date
 df.sort_values('date', inplace=True)
 df.reset_index(drop=True, inplace=True)

 # Forward-fill then back-fill small gaps in price columns
 df[price_cols] = df[price_cols].ffill().bfill()

 # Drop rows where date or close is still NaN
 df.dropna(subset=['date', 'close'], inplace=True)

 # Daily return (percentage change of close price)
 df['daily_return'] = df['close'].pct_change() * 100 # in percent

 # Ticker label
 df['ticker'] = ticker

 return df


def load_and_clean_all_stocks(
 tickers: list = STOCK_TICKERS,
 raw_dir: str = RAW_DIR,
) -> pd.DataFrame:
 """Load, clean, and concatenate all stock DataFrames."""
 frames = []
 for t in tickers:
  raw = load_raw_stock(t, raw_dir)
  clean = clean_stock(raw, t)
  frames.append(clean)
 return pd.concat(frames, ignore_index=True)

# ---------------------------------------------------------------------------
# Mutual fund data
# ---------------------------------------------------------------------------

def load_raw_mutual_funds(raw_dir: str = RAW_DIR) -> pd.DataFrame:
 """Load the comprehensive mutual funds CSV."""
 path = os.path.join(raw_dir, 'comprehensive_mutual_funds_data.csv')
 if not os.path.exists(path):
  raise FileNotFoundError(f"Mutual funds data not found: {path}")
 return pd.read_csv(path)


def clean_mutual_funds(df: pd.DataFrame) -> pd.DataFrame:
 """
 Clean the mutual funds DataFrame:
  1. Standardize column names
  2. Convert numeric columns
  3. Handle missing values
  4. Standardize category names
 """
 df = df.copy()
 df = _standardize_columns(df)

 # Numeric columns
 numeric_cols = [
  'min_sip', 'min_lumpsum', 'expense_ratio', 'fund_size_cr',
  'fund_age_yr', 'sortino', 'alpha', 'sd', 'beta', 'sharpe',
  'rating', 'returns_1yr', 'returns_3yr', 'returns_5yr',
 ]
 for col in numeric_cols:
  if col in df.columns:
   df[col] = pd.to_numeric(df[col], errors='coerce')

 # Standardize text columns
 for col in ['category', 'sub_category', 'risk_level', 'amc_name']:
  if col in df.columns:
   df[col] = df[col].astype(str).str.strip().str.title()

 # Fill missing numeric with median (column-wise)
 for col in numeric_cols:
  if col in df.columns:
   df[col].fillna(df[col].median(), inplace=True)

 # Drop rows where scheme_name is missing
 df.dropna(subset=['scheme_name'], inplace=True)
 df.reset_index(drop=True, inplace=True)

 return df

# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def save_processed(df: pd.DataFrame, filename: str, processed_dir: str = PROCESSED_DIR):
 """Save a DataFrame to the processed/ directory."""
 os.makedirs(processed_dir, exist_ok=True)
 out = os.path.join(processed_dir, filename)
 df.to_csv(out, index=False)
 print(f"✓ Saved → {out} ({len(df)} rows)")
 return out


def build_all(raw_dir: str = RAW_DIR, processed_dir: str = PROCESSED_DIR):
 """End-to-end: load, clean, save all datasets."""
 print("=" * 60)
 print(" Financial Data Processing Pipeline")
 print("=" * 60)

 # Stocks
 print("\n Processing stock data …")
 stocks = load_and_clean_all_stocks(raw_dir=raw_dir)
 save_processed(stocks, 'all_stocks_clean.csv', processed_dir)

 # Individual stock files
 for ticker in STOCK_TICKERS:
  subset = stocks[stocks['ticker'] == ticker]
  save_processed(subset, f'{ticker}_clean.csv', processed_dir)

 # Mutual funds
 print("\n Processing mutual fund data …")
 mf_raw = load_raw_mutual_funds(raw_dir)
 mf_clean = clean_mutual_funds(mf_raw)
 save_processed(mf_clean, 'mutual_funds_clean.csv', processed_dir)

 # Dashboard-ready exports
 print("\n Creating dashboard-ready exports …")
 _export_dashboard_data(stocks, mf_clean, processed_dir)

 print("\n Pipeline complete.")
 return stocks, mf_clean


def _export_dashboard_data(stocks: pd.DataFrame, mf: pd.DataFrame, out_dir: str):
 """Create summary CSVs optimised for Power BI / Streamlit."""
 # Stock summary table
 summary = (
  stocks.groupby('ticker')
  .agg(
   avg_close=('close', 'mean'),
   avg_daily_return=('daily_return', 'mean'),
   volatility=('daily_return', 'std'),
   min_date=('date', 'min'),
   max_date=('date', 'max'),
   total_records=('close', 'count'),
  )
  .reset_index()
 )
 save_processed(summary, 'stock_summary.csv', out_dir)

 # MF category summary
 cat_summary = (
  mf.groupby('category')
  .agg(
   count=('scheme_name', 'count'),
   avg_return_1yr=('returns_1yr', 'mean'),
   avg_return_3yr=('returns_3yr', 'mean'),
   avg_return_5yr=('returns_5yr', 'mean'),
   avg_risk=('sd', 'mean'),
  )
  .reset_index()
 )
 save_processed(cat_summary, 'mf_category_summary.csv', out_dir)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
 build_all()
