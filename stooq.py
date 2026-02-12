import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# current_positions = pd.read_csv("Individual-Positions-2024-06-20-160845.csv")
current_positions = pd.read_csv("dummy_positions.csv")
current_positions['symbol']
current_positions['quantity']
current_positions['cost_basis']


def fetch_stooq(ticker):
    """
    Fetch full historical daily data from Stooq.
    """
    url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=d"
    df = pd.read_csv(url)
    if "Date" not in df.columns:
        print(f"⚠️ No data for {ticker}")
        return None
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df.set_index("Date", inplace=True)
    return df


def fetch_many_stooq(tickers):
    data = {}
    for ticker in tickers:
        df = fetch_stooq(ticker)
        if df is not None:
            data[ticker] = df["Close"]
    return pd.DataFrame(data)


def build_portfolio_history(positions_df, prices):
    """
    positions_df: DataFrame with columns ['symbol', 'quantity', 'cost_basis']
    prices: DataFrame of Close prices indexed by Date, columns = tickers
    """
    # Align quantities by symbol
    quantities = (
        positions_df
        .set_index("symbol")["quantity"]
    )
    # Ensure prices only include symbols we own
    prices = prices[quantities.index]
    # Multiply prices by share quantities (broadcast across columns)
    portfolio = prices.mul(quantities, axis=1)
    # Add total portfolio value
    portfolio["Total"] = portfolio.sum(axis=1)
    return portfolio



# Example: only first 3 positions
subset = current_positions
prices = fetch_many_stooq(subset["symbol"])
portfolio = build_portfolio_history(subset, prices)


def plot_price_vs_cost_grid(positions_df, prices, ncols=3):
    n = len(positions_df)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 3.5*nrows))
    axes = np.array(axes).reshape(-1)
    for i, row in enumerate(positions_df.itertuples()):
        ax = axes[i]
        symbol = row.symbol
        cost = row.cost_basis
        description = row.description
        pct_return = row.pct_return
        total_gain = row.total_gain
        # Skip if price missing
        if symbol not in prices.columns:
            ax.set_visible(False)
            continue
        price_series = prices[symbol]
        # Plot price
        line_price, = ax.plot(price_series.index, price_series)
        # Cost basis line
        ax.axhline(
            y=cost,
            color=line_price.get_color(),
            linestyle="--",
            linewidth=2
        )
        # Green / Red shading
        ax.fill_between(
            price_series.index,
            price_series,
            cost,
            where=(price_series >= cost),
            color="green",
            alpha=0.15
        )
        ax.fill_between(
            price_series.index,
            price_series,
            cost,
            where=(price_series < cost),
            color="red",
            alpha=0.15
        )
        ax.set_title(
            f"{symbol} | {description}\n"
            f"${total_gain:,.0f}  ({pct_return:.1%})"
        )
        ax.grid(alpha=0.3)
    # Remove unused axes
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    plt.tight_layout()
    plt.show()

def add_current_performance(positions_df, prices):
    df = positions_df.copy()
    # Get latest price for each symbol
    latest_prices = prices.iloc[-1]
    # Map latest prices into positions_df
    df["current_price"] = df["symbol"].map(latest_prices)
    # Absolute difference
    df["price_diff"] = df["current_price"] - df["cost_basis"]
    # Percent return
    df["pct_return"] = df["price_diff"] / df["cost_basis"]
    # Total P/L
    df["total_gain"] = df["price_diff"] * df["quantity"]
    return df


subset_perf = add_current_performance(current_positions, prices)
subset_sorted = subset_perf.sort_values("price_diff", ascending=False)
subset_sorted = subset_perf.sort_values("total_gain", ascending=False)

prices = fetch_many_stooq(subset_sorted["symbol"])
filtered_prices = prices.loc["2010-01-01":]
subset_sorted = subset_sorted[(subset_sorted['symbol'] != 'BYDDY') & (subset_sorted['symbol'] != 'VWAGY')]
plot_price_vs_cost_grid(subset_sorted, filtered_prices, ncols=3)





