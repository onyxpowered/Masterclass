from pathlib import Path

import yfinance as yf

TICKERS = ["SPY", "QQQ", "IWM"]
START = "2010-01-01"
DATA_DIR = Path(__file__).parent / "data"


def fetch(ticker):
    bars = yf.download(ticker, start=START, auto_adjust=True, progress=False)
    bars.columns = [col[0] for col in bars.columns]
    bars.index.name = "Date"
    return bars[["Open", "High", "Low", "Close", "Volume"]].dropna()


def main():
    DATA_DIR.mkdir(exist_ok=True)
    for ticker in TICKERS:
        bars = fetch(ticker)
        bars.to_csv(DATA_DIR / f"{ticker}.csv")
        print(f"{ticker}: {len(bars)} bars, {bars.index[0].date()} to {bars.index[-1].date()}")


if __name__ == "__main__":
    main()
