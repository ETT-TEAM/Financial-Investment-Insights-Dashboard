"""
metrics.py — Financial Metrics Computation
============================================
Computes average return, volatility (standard deviation),
risk-return ratios, and comparative analysis for stocks
and mutual funds.
"""

import pandas as pd
import numpy as np
from typing import Dict, List


# ---------------------------------------------------------------------------
# Stock-level metrics
# ---------------------------------------------------------------------------

def compute_stock_metrics(stocks_df: pd.DataFrame) -> pd.DataFrame:
 """
 Compute per-ticker financial metrics from a cleaned stock DataFrame.

 Returns DataFrame with columns:
  ticker, avg_daily_return, volatility, sharpe_proxy,
  cumulative_return, avg_close
 """
 results = []
 for ticker, grp in stocks_df.groupby('ticker'):
  daily_ret = grp['daily_return'].dropna()
  avg_ret = daily_ret.mean()
  vol = daily_ret.std()
  sharpe = avg_ret / vol if vol != 0 else 0

  # Cumulative return (first → last close)
  first_close = grp['close'].iloc[0]
  last_close = grp['close'].iloc[-1]
  cum_ret = ((last_close - first_close) / first_close) * 100

  results.append({
   'ticker': ticker,
   'avg_daily_return': round(avg_ret, 4),
   'volatility': round(vol, 4),
   'sharpe_proxy': round(sharpe, 4),
   'cumulative_return_pct': round(cum_ret, 2),
   'avg_close': round(grp['close'].mean(), 2),
  })

 return pd.DataFrame(results)


def risk_return_comparison(metrics_df: pd.DataFrame) -> Dict:
 """
 Identify the highest-return and lowest-risk stocks.

 Returns a dict with keys:
  highest_return, lowest_risk, best_sharpe
 """
 highest_ret = metrics_df.loc[metrics_df['avg_daily_return'].idxmax()]
 lowest_risk = metrics_df.loc[metrics_df['volatility'].idxmin()]
 best_sharpe = metrics_df.loc[metrics_df['sharpe_proxy'].idxmax()]

 return {
  'highest_return': {
   'ticker': highest_ret['ticker'],
   'avg_daily_return': highest_ret['avg_daily_return'],
  },
  'lowest_risk': {
   'ticker': lowest_risk['ticker'],
   'volatility': lowest_risk['volatility'],
  },
  'best_sharpe': {
   'ticker': best_sharpe['ticker'],
   'sharpe_proxy': best_sharpe['sharpe_proxy'],
  },
 }


# ---------------------------------------------------------------------------
# Mutual fund metrics
# ---------------------------------------------------------------------------

def compute_mf_metrics(mf_df: pd.DataFrame) -> pd.DataFrame:
 """
 Compute per-category mutual fund summary metrics.

 Returns DataFrame with columns:
  category, avg_return_1yr, avg_return_3yr, avg_return_5yr,
  avg_risk, count, best_fund
 """
 results = []
 for cat, grp in mf_df.groupby('category'):
  best_idx = grp['returns_1yr'].idxmax()
  best_fund = grp.loc[best_idx, 'scheme_name'] if pd.notna(best_idx) else 'N/A'

  results.append({
   'category': cat,
   'count': len(grp),
   'avg_return_1yr': round(grp['returns_1yr'].mean(), 2),
   'avg_return_3yr': round(grp['returns_3yr'].mean(), 2),
   'avg_return_5yr': round(grp['returns_5yr'].mean(), 2),
   'avg_risk': round(grp['sd'].mean(), 2),
   'best_fund': best_fund,
  })

 return pd.DataFrame(results)


def top_mutual_funds(
 mf_df: pd.DataFrame,
 by: str = 'returns_1yr',
 n: int = 10,
) -> pd.DataFrame:
 """Return the top-n mutual funds sorted by the given column."""
 return (
  mf_df
  .nlargest(n, by)
  [['scheme_name', 'category', 'returns_1yr', 'returns_3yr',
   'returns_5yr', 'sd', 'risk_level', 'rating']]
  .reset_index(drop=True)
 )


def mf_risk_return_analysis(mf_df: pd.DataFrame) -> Dict:
 """Analyse mutual fund risk-return relationship."""
 correlation = mf_df[['sd', 'returns_1yr']].dropna().corr().iloc[0, 1]
 avg_by_risk = (
  mf_df
  .groupby('risk_level')[['returns_1yr', 'sd']]
  .mean()
  .round(2)
  .to_dict('index')
 )
 return {
  'risk_return_correlation': round(correlation, 4),
  'avg_by_risk_level': avg_by_risk,
 }


# ---------------------------------------------------------------------------
# Quick summary printer
# ---------------------------------------------------------------------------

def print_summary(stocks_df: pd.DataFrame, mf_df: pd.DataFrame):
 """Pretty-print key financial metrics."""
 print("=" * 60)
 print(" FINANCIAL METRICS SUMMARY")
 print("=" * 60)

 sm = compute_stock_metrics(stocks_df)
 print("\n Stock Metrics")
 print(sm.to_string(index=False))

 rr = risk_return_comparison(sm)
 print(f"\n → Highest return : {rr['highest_return']['ticker']} "
   f"({rr['highest_return']['avg_daily_return']}%)")
 print(f" → Lowest risk : {rr['lowest_risk']['ticker']} "
   f"(σ = {rr['lowest_risk']['volatility']})")
 print(f" → Best Sharpe : {rr['best_sharpe']['ticker']} "
   f"({rr['best_sharpe']['sharpe_proxy']})")

 mm = compute_mf_metrics(mf_df)
 print("\n Mutual Fund Category Metrics")
 print(mm[['category', 'count', 'avg_return_1yr', 'avg_risk']].to_string(index=False))

 mra = mf_risk_return_analysis(mf_df)
 print(f"\n → Risk-Return correlation: {mra['risk_return_correlation']}")

 print("\n Summary complete.")


if __name__ == '__main__':
 from data_processing import load_and_clean_all_stocks, load_raw_mutual_funds, clean_mutual_funds
 stocks = load_and_clean_all_stocks()
 mf = clean_mutual_funds(load_raw_mutual_funds())
 print_summary(stocks, mf)
