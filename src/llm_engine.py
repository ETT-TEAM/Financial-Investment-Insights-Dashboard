"""
llm_engine.py — Real LLM-Powered Insight Generator
=====================================================
Upgrades the rule-based InsightEngine by using Ollama
(llama3) to generate genuine AI-powered natural language
financial insights. Drop-in compatible with app.py.


"""

import ollama
import pandas as pd
from typing import Dict


# ═══════════════════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════════════════

def _ask(prompt: str, model: str = "llama3") -> str:
    """Send a prompt to Ollama and return the response."""
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ LLM unavailable: {str(e)}. Please ensure Ollama is running."


# ═══════════════════════════════════════════════════════════════
# LLM INSIGHT ENGINE
# ═══════════════════════════════════════════════════════════════

class LLMInsightEngine:
    """
    AI-powered insight engine using Ollama (llama3).
    Accepts the same inputs as InsightEngine for
    drop-in compatibility with app.py.

    Usage:
        engine = LLMInsightEngine(stock_metrics_df, mf_df)
        insights = engine.generate_dict()
    """

    def __init__(
        self,
        stock_metrics: pd.DataFrame,
        mf_df: pd.DataFrame,
        stock_data: pd.DataFrame = None,
        model: str = "llama3"
    ):
        self.sm = stock_metrics.copy()
        self.mf = mf_df.copy()
        self.stock_data = stock_data
        self.model = model

    # ────────────────────────────────────────────────────────────
    # Stock Insights
    # ────────────────────────────────────────────────────────────

    def market_overview(self) -> str:
        avg_ret = self.sm['avg_daily_return'].mean()
        avg_vol = self.sm['volatility'].mean()
        tickers = ", ".join(self.sm['ticker'].tolist())

        prompt = f"""You are a financial educator explaining stock market data to a beginner investor.

Here is the data for the analysed stocks ({tickers}):
- Average daily return: {avg_ret:.4f}%
- Average volatility (σ): {avg_vol:.4f}%

In exactly 3-4 plain English sentences, explain what this data means for someone new to investing.
Rules:
- No buy or sell advice
- No predictions about future performance
- No financial jargon without explanation
- Be concise and friendly"""

        return _ask(prompt, self.model)

    def highest_return_stock(self) -> str:
        row = self.sm.loc[self.sm['avg_daily_return'].idxmax()]
        ticker = row['ticker']
        ret = row['avg_daily_return']
        vol = row['volatility']
        sharpe = row['sharpe_proxy']

        prompt = f"""You are a financial educator explaining stock data to a beginner.

{ticker} has the highest average daily return among the analysed stocks:
- Average daily return: {ret:.4f}%
- Volatility (σ): {vol:.4f}%
- Risk-adjusted return (Sharpe proxy): {sharpe:.4f}

In 3 plain English sentences, explain what these numbers mean and whether the return justifies the risk.
No predictions, no buy/sell advice."""

        return _ask(prompt, self.model)

    def lowest_risk_stock(self) -> str:
        row = self.sm.loc[self.sm['volatility'].idxmin()]
        ticker = row['ticker']
        vol = row['volatility']
        ret = row['avg_daily_return']

        prompt = f"""You are a financial educator explaining stock data to a beginner investor.

{ticker} has the lowest volatility among the analysed stocks:
- Volatility (σ): {vol:.4f}%
- Average daily return: {ret:.4f}%

In 3 plain English sentences, explain what low volatility means and why it matters for investors.
No predictions, no buy/sell advice."""

        return _ask(prompt, self.model)

    def risk_return_tradeoff(self) -> str:
        corr = self.sm[['avg_daily_return', 'volatility']].corr().iloc[0, 1]
        best_sharpe = self.sm.loc[self.sm['sharpe_proxy'].idxmax()]

        prompt = f"""You are a financial educator explaining the risk-return tradeoff to a beginner.

Among the analysed stocks:
- Correlation between return and volatility: {corr:.2f}
- Best risk-adjusted stock: {best_sharpe['ticker']} 
  with Sharpe proxy of {best_sharpe['sharpe_proxy']:.4f}

In 3-4 plain English sentences, explain what the correlation means and why 
{best_sharpe['ticker']} stands out on a risk-adjusted basis.
No predictions, no buy/sell advice."""

        return _ask(prompt, self.model)

    def cumulative_performance(self) -> str:
        best = self.sm.loc[self.sm['cumulative_return_pct'].idxmax()]
        worst = self.sm.loc[self.sm['cumulative_return_pct'].idxmin()]

        prompt = f"""You are a financial educator explaining cumulative stock performance to a beginner.

Over the analysis period:
- Best performer: {best['ticker']} with {best['cumulative_return_pct']:.1f}% cumulative return
- Weakest performer: {worst['ticker']} with {worst['cumulative_return_pct']:.1f}% cumulative return

In 3 plain English sentences, explain what cumulative return means and what this difference tells us.
No predictions, no buy/sell advice."""

        return _ask(prompt, self.model)

    # ────────────────────────────────────────────────────────────
    # Mutual Fund Insights
    # ────────────────────────────────────────────────────────────

    def mf_top_performers(self, n: int = 3) -> str:
        top = self.mf.nlargest(n, 'returns_1yr')[
            ['scheme_name', 'returns_1yr', 'sd']
        ].dropna()
        data_str = top.to_string(index=False)

        prompt = f"""You are a financial educator explaining mutual fund data to a beginner investor.

Here are the top {n} mutual funds by 1-year return:
{data_str}

In 3-4 plain English sentences, summarise what makes these funds stand out 
and what the risk (sd) column tells us about each one.
No predictions, no buy/sell advice."""

        return _ask(prompt, self.model)

    def mf_category_analysis(self) -> str:
        cat_avg = (
            self.mf.groupby('category')
            .agg(avg_ret=('returns_1yr', 'mean'), avg_risk=('sd', 'mean'))
            .reset_index()
            .dropna()
        )
        if cat_avg.empty:
            return "Insufficient category data for analysis."

        best_cat = cat_avg.loc[cat_avg['avg_ret'].idxmax()]
        safest_cat = cat_avg.loc[cat_avg['avg_risk'].idxmin()]

        prompt = f"""You are a financial educator explaining mutual fund categories to a beginner.

Among all mutual fund categories analysed:
- Highest returning category: {best_cat['category']} 
  with average 1-year return of {best_cat['avg_ret']:.1f}%
- Lowest risk category: {safest_cat['category']} 
  with average risk (σ) of {safest_cat['avg_risk']:.1f}

In 3-4 plain English sentences, explain what these categories mean for 
different types of investors — both risk-tolerant and conservative.
No predictions, no buy/sell advice."""

        return _ask(prompt, self.model)

    def mf_risk_return_insight(self) -> str:
        corr = self.mf[['sd', 'returns_1yr']].dropna().corr().iloc[0, 1]

        prompt = f"""You are a financial educator explaining mutual fund risk and return to a beginner.

The correlation between mutual fund risk (standard deviation) and 1-year return is: {corr:.2f}

In 3 plain English sentences, explain what this correlation value means —
does taking more risk lead to better returns in mutual funds?
No predictions, no buy/sell advice."""

        return _ask(prompt, self.model)

    def mf_long_term_consistency(self) -> str:
        avg_1yr = self.mf['returns_1yr'].mean()
        avg_3yr = self.mf['returns_3yr'].mean() if 'returns_3yr' in self.mf else None
        avg_5yr = self.mf['returns_5yr'].mean() if 'returns_5yr' in self.mf else None

        prompt = f"""You are a financial educator explaining long-term mutual fund performance to a beginner.

Average mutual fund returns across time periods:
- 1-year average return: {avg_1yr:.1f}%
- 3-year average return: {avg_3yr:.1f}% 
- 5-year average return: {avg_5yr:.1f}%

In 3-4 plain English sentences, explain what this trend means for 
short-term vs long-term investors.
No predictions, no buy/sell advice."""

        return _ask(prompt, self.model)

    # ────────────────────────────────────────────────────────────
    # Aggregate
    # ────────────────────────────────────────────────────────────

    def generate_dict(self) -> Dict[str, str]:
        """
        Returns all insights as a dictionary.
        Compatible with app.py's existing generate_dict() usage.
        Note: Takes ~30-60 seconds as each insight calls Ollama.
        """
        print("🤖 Generating AI insights via Ollama... please wait.")
        return {
            'market_overview':        self.market_overview(),
            'highest_return_stock':   self.highest_return_stock(),
            'lowest_risk_stock':      self.lowest_risk_stock(),
            'risk_return_tradeoff':   self.risk_return_tradeoff(),
            'cumulative_performance': self.cumulative_performance(),
            'mf_top_performers':      self.mf_top_performers(),
            'mf_category_analysis':   self.mf_category_analysis(),
            'mf_risk_return_insight': self.mf_risk_return_insight(),
            'mf_long_term_consistency': self.mf_long_term_consistency(),
        }

    def generate_report(self) -> str:
        """Returns all insights as a single formatted string."""
        insights = self.generate_dict()
        lines = [
            "=" * 60,
            "🤖 AI-GENERATED FINANCIAL INSIGHTS (Powered by Ollama)",
            "=" * 60,
            "",
        ]
        for key, value in insights.items():
            title = key.replace('_', ' ').title()
            lines.append(f"── {title} ──")
            lines.append(value)
            lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from data_processing import load_and_clean_all_stocks, load_raw_mutual_funds, clean_mutual_funds
    from metrics import compute_stock_metrics

    print("Loading data...")
    stocks = load_and_clean_all_stocks()
    mf = clean_mutual_funds(load_raw_mutual_funds())
    sm = compute_stock_metrics(stocks)

    print("Starting LLM engine...\n")
    engine = LLMInsightEngine(sm, mf, stocks)
    print(engine.market_overview())