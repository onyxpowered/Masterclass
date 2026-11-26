import numpy as np
import pandas as pd

from data import load_bars

TICKERS = ["SPY", "QQQ", "IWM"]
START_CASH = 50.0
COST = 0.0005
FAST = 20
SLOW = 50
TRADING_DAYS = 252


def crossover_signal(bars, fast=FAST, slow=SLOW):
    close = bars["Close"]
    return (close.rolling(fast).mean() > close.rolling(slow).mean()).astype(int)


def run(bars, signal, cost=COST, start_cash=START_CASH):
    position = signal.shift(1).fillna(0)
    period_return = bars["Open"].shift(-1) / bars["Open"] - 1
    trades = position.diff().abs().fillna(0)
    strategy_return = position * period_return - trades * cost
    frame = pd.DataFrame(
        {
            "position": position,
            "trades": trades,
            "strategy": strategy_return,
            "buyhold": period_return,
        }
    ).dropna()
    frame["equity"] = start_cash * (1 + frame["strategy"]).cumprod()
    frame["benchmark"] = start_cash * (1 + frame["buyhold"]).cumprod()
    return frame


def summarize(equity, returns, start_cash=START_CASH):
    years = len(returns) / TRADING_DAYS
    final = equity.iloc[-1]
    return {
        "final $": round(final, 2),
        "CAGR %": round(((final / start_cash) ** (1 / years) - 1) * 100, 2),
        "max drawdown %": round((equity / equity.cummax() - 1).min() * 100, 2),
        "Sharpe": round(returns.mean() / returns.std() * np.sqrt(TRADING_DAYS), 2),
    }


def main():
    for ticker in TICKERS:
        bars = load_bars(ticker)
        frame = run(bars, crossover_signal(bars))
        table = pd.DataFrame(
            {
                f"{FAST}/{SLOW} crossover": summarize(frame["equity"], frame["strategy"]),
                "buy and hold": summarize(frame["benchmark"], frame["buyhold"]),
            }
        )
        print(f"\n{ticker}  {frame.index[0].date()} to {frame.index[-1].date()}")
        print(table.to_string())
        print(f"position changes: {int(frame['trades'].sum())}, time invested: {frame['position'].mean():.0%}")


if __name__ == "__main__":
    main()
