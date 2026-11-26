from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
PRICES = ["Open", "High", "Low", "Close"]
TOLERANCE = 1e-6
EXTREME_MOVE = 0.25


def validate(bars):
    problems = []
    if bars.isna().any().any():
        problems.append("missing values")
    if not bars.index.is_monotonic_increasing:
        problems.append("dates out of order")
    if bars.index.has_duplicates:
        problems.append("duplicate dates")
    if (bars[PRICES] <= 0).any().any():
        problems.append("non-positive prices")
    highs_too_low = bars["High"] < bars[["Open", "Close"]].max(axis=1) * (1 - TOLERANCE)
    if highs_too_low.any():
        problems.append(f"{int(highs_too_low.sum())} bars where High is below Open or Close")
    lows_too_high = bars["Low"] > bars[["Open", "Close"]].min(axis=1) * (1 + TOLERANCE)
    if lows_too_high.any():
        problems.append(f"{int(lows_too_high.sum())} bars where Low is above Open or Close")
    if (bars["High"] < bars["Low"]).any():
        problems.append("bars where High is below Low")
    extreme = bars["Close"].pct_change().abs() > EXTREME_MOVE
    if extreme.any():
        problems.append(f"{int(extreme.sum())} daily moves over {EXTREME_MOVE:.0%}")
    return problems


def load_bars(ticker):
    bars = pd.read_csv(DATA_DIR / f"{ticker}.csv", index_col="Date", parse_dates=True)
    today = pd.Timestamp.today().normalize()
    bars = bars[bars.index < today]
    problems = validate(bars)
    if problems:
        raise ValueError(f"{ticker}: " + "; ".join(problems))
    return bars


if __name__ == "__main__":
    for path in sorted(DATA_DIR.glob("*.csv")):
        ticker = path.stem
        try:
            bars = load_bars(ticker)
            print(f"{ticker}: OK, {len(bars)} complete bars, last {bars.index[-1].date()}")
        except ValueError as error:
            print(f"FAILED {error}")
