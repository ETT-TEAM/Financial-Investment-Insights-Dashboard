"""
insight_engine.py — LLM-Inspired Rule-Based Insight Generator
===============================================================
Generates human-readable, natural-language financial insights
using deterministic rules that mimic LLM output style. Each
function analyses a specific aspect and returns plain-English
sentences suitable for display in a dashboard or report.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# INSIGHT GENERATOR CLASS
# ═══════════════════════════════════════════════════════════════

class InsightEngine:
 """
 A rule-based engine that produces LLM-style financial insights.

 Usage:
  engine = InsightEngine(stock_metrics_df, mf_df)
  insights = engine.generate_all()
  for i in insights:
   print(i)
 """

 def __init__(
  self,
  stock_metrics: pd.DataFrame,
  mf_df: pd.DataFrame,
  stock_data: pd.DataFrame | None = None,
 ):
  """
  Parameters
  ----------
  stock_metrics : DataFrame with columns
   ticker, avg_daily_return, volatility, sharpe_proxy, cumulative_return_pct
  mf_df : Cleaned mutual funds DataFrame
  stock_data : (optional) Full daily stock DataFrame for trend analysis
  """
  self.sm = stock_metrics.copy()
  self.mf = mf_df.copy()
  self.stock_data = stock_data

 # ────────────────────────────────────────────────────────────
 # Stock insights
 # ────────────────────────────────────────────────────────────

 def highest_return_stock(self) -> str:
  """Identify and describe the highest-return stock."""
  row = self.sm.loc[self.sm['avg_daily_return'].idxmax()]
  ticker = row['ticker']
  ret = row['avg_daily_return']
  vol = row['volatility']

  qualifier = "with moderate volatility" if vol < self.sm['volatility'].median() \
     else "accompanied by higher volatility"

  return (
   f" {ticker} delivers the highest average daily return of "
   f"{ret:.4f}%, {qualifier} (σ = {vol:.4f}%). "
   f"This suggests strong upward momentum but investors should "
   f"be mindful of the associated risk."
  )

 def lowest_risk_stock(self) -> str:
  """Identify and describe the lowest-risk stock."""
  row = self.sm.loc[self.sm['volatility'].idxmin()]
  ticker = row['ticker']
  vol = row['volatility']
  ret = row['avg_daily_return']

  return (
   f" {ticker} exhibits the lowest volatility (σ = {vol:.4f}%), "
   f"making it the most stable investment among the analysed stocks. "
   f"Its average daily return is {ret:.4f}%, offering a "
   f"{'favourable' if ret > 0 else 'modest'} return with lower risk."
  )

 def risk_return_tradeoff(self) -> str:
  """Explain the risk-return tradeoff across stocks."""
  corr = self.sm[['avg_daily_return', 'volatility']].corr().iloc[0, 1]
  direction = "positive" if corr > 0 else "negative"
  strength = (
   "strong" if abs(corr) > 0.7 else
   "moderate" if abs(corr) > 0.4 else
   "weak"
  )

  best_sharpe = self.sm.loc[self.sm['sharpe_proxy'].idxmax()]

  return (
   f" The risk-return tradeoff shows a {strength} {direction} "
   f"correlation (r = {corr:.2f}). Higher-risk investments tend to "
   f"{'yield higher returns' if corr > 0 else 'not necessarily yield higher returns'}. "
   f"{best_sharpe['ticker']} offers the best risk-adjusted return "
   f"(Sharpe proxy = {best_sharpe['sharpe_proxy']:.4f}), balancing "
   f"return against volatility most efficiently."
  )

 def cumulative_performance(self) -> str:
  """Summarise cumulative returns."""
  best = self.sm.loc[self.sm['cumulative_return_pct'].idxmax()]
  worst = self.sm.loc[self.sm['cumulative_return_pct'].idxmin()]

  return (
   f" Over the entire analysis period, {best['ticker']} achieved "
   f"the highest cumulative return of {best['cumulative_return_pct']:.1f}%, "
   f"while {worst['ticker']} recorded {worst['cumulative_return_pct']:.1f}%. "
   f"Long-term investors in {best['ticker']} would have seen the "
   f"greatest portfolio growth."
  )

 # ────────────────────────────────────────────────────────────
 # Mutual fund insights
 # ────────────────────────────────────────────────────────────

 def mf_top_performers(self, n: int = 3) -> str:
  """Highlight top-performing mutual funds."""
  top = self.mf.nlargest(n, 'returns_1yr')
  lines = []
  for _, row in top.iterrows():
   lines.append(
    f" • {row['scheme_name']} — "
    f"1-yr: {row['returns_1yr']:.1f}%, "
    f"risk(σ): {row['sd']:.1f}"
   )
  header = f" Top {n} Mutual Funds by 1-Year Return:\n"
  return header + "\n".join(lines)

 def mf_category_analysis(self) -> str:
  """Analyse mutual fund performance by category."""
  cat_avg = (
   self.mf.groupby('category')
   .agg(avg_ret=('returns_1yr', 'mean'), avg_risk=('sd', 'mean'))
   .reset_index()
  )
  best_cat = cat_avg.loc[cat_avg['avg_ret'].idxmax()]
  safest_cat = cat_avg.loc[cat_avg['avg_risk'].idxmin()]

  return (
   f" Among mutual fund categories, '{best_cat['category']}' "
   f"leads with an average 1-year return of {best_cat['avg_ret']:.1f}%. "
   f"'{safest_cat['category']}' offers the lowest average risk "
   f"(σ = {safest_cat['avg_risk']:.1f}), making it suitable for "
   f"conservative investors."
  )

 def mf_risk_return_insight(self) -> str:
  """Explain mutual fund risk-return relationship."""
  corr = self.mf[['sd', 'returns_1yr']].dropna().corr().iloc[0, 1]
  direction = "positive" if corr > 0 else "inverse"

  return (
   f" Mutual fund risk and return show a {direction} correlation "
   f"(r = {corr:.2f}). "
   f"{'Funds with higher risk tend to deliver higher returns, ' if corr > 0 else 'Interestingly, higher risk does not guarantee higher returns, '}"
   f"suggesting that {'risk-tolerant investors may be rewarded' if corr > 0 else 'careful fund selection is more important than risk-taking'}."
  )

 def mf_long_term_consistency(self) -> str:
  """Analyse consistency of returns over 1yr, 3yr, 5yr."""
  cols = ['returns_1yr', 'returns_3yr', 'returns_5yr']
  available = [c for c in cols if c in self.mf.columns]
  if len(available) < 2:
   return " Insufficient multi-period return data for consistency analysis."

  avgs = {c: self.mf[c].mean() for c in available}
  trend = "improving" if avgs.get('returns_1yr', 0) > avgs.get('returns_5yr', 0) \
    else "declining"

  return (
   f" Mutual fund returns have been {trend} over time: "
   f"5-year avg = {avgs.get('returns_5yr', 0):.1f}%, "
   f"3-year avg = {avgs.get('returns_3yr', 0):.1f}%, "
   f"1-year avg = {avgs.get('returns_1yr', 0):.1f}%. "
   f"{'Short-term momentum is strong.' if trend == 'improving' else 'Long-term investors have benefited from earlier entry points.'}"
  )

 # ────────────────────────────────────────────────────────────
 # Market overview
 # ────────────────────────────────────────────────────────────

 def market_overview(self) -> str:
  """Generate a high-level market overview paragraph."""
  avg_ret = self.sm['avg_daily_return'].mean()
  avg_vol = self.sm['volatility'].mean()
  market_mood = "bullish" if avg_ret > 0 else "bearish"
  vol_level = "elevated" if avg_vol > 2 else "moderate" if avg_vol > 1 else "low"

  return (
   f" Market Overview: The analysed stocks show an average daily "
   f"return of {avg_ret:.4f}% with {vol_level} volatility "
   f"(avg σ = {avg_vol:.4f}%). Overall market sentiment appears "
   f"{market_mood}. Diversification across the analysed assets can "
   f"help mitigate individual stock risk."
  )

 # ────────────────────────────────────────────────────────────
 # Aggregate
 # ────────────────────────────────────────────────────────────

 def generate_all(self) -> List[str]:
  """Generate all insights in a structured list."""
  return [
   "═" * 60,
   " AI-GENERATED FINANCIAL INSIGHTS",
   f" Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
   "═" * 60,
   "",
   "── Stock Analysis ──────────────────────────────────",
   self.market_overview(),
   "",
   self.highest_return_stock(),
   "",
   self.lowest_risk_stock(),
   "",
   self.risk_return_tradeoff(),
   "",
   self.cumulative_performance(),
   "",
   "── Mutual Fund Analysis ────────────────────────────",
   self.mf_top_performers(),
   "",
   self.mf_category_analysis(),
   "",
   self.mf_risk_return_insight(),
   "",
   self.mf_long_term_consistency(),
   "",
   "═" * 60,
  ]

 def generate_report(self) -> str:
  """Return all insights as a single formatted string."""
  return "\n".join(self.generate_all())

 def generate_dict(self) -> Dict[str, str]:
  """Return insights as a dictionary (useful for dashboards)."""
  return {
   'market_overview': self.market_overview(),
   'highest_return_stock': self.highest_return_stock(),
   'lowest_risk_stock': self.lowest_risk_stock(),
   'risk_return_tradeoff': self.risk_return_tradeoff(),
   'cumulative_performance': self.cumulative_performance(),
   'mf_top_performers': self.mf_top_performers(),
   'mf_category_analysis': self.mf_category_analysis(),
   'mf_risk_return_insight': self.mf_risk_return_insight(),
   'mf_long_term_consistency': self.mf_long_term_consistency(),
  }


# ═══════════════════════════════════════════════════════════════
# CLI demo
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
 from data_processing import load_and_clean_all_stocks, load_raw_mutual_funds, clean_mutual_funds
 from metrics import compute_stock_metrics

 stocks = load_and_clean_all_stocks()
 mf = clean_mutual_funds(load_raw_mutual_funds())
 sm = compute_stock_metrics(stocks)

 engine = InsightEngine(sm, mf, stocks)
 print(engine.generate_report())
