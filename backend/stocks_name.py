import pandas as pd

# Load CSV (replace with your actual filename or URL)
df = pd.read_csv("nse_stock_symbols.csv")

# Define keywords that indicate non-equity instruments
non_eq_keywords = ['ETF', 'AMC', 'IETF', 'FUND', 'INDEX', 'BEES', 'QUAL', 'SILVER', 'LOWVOL', 'MOMENT', 'VALUE', 'NIFTY', 'SENSEX']

# Filter out any row where the Stock Name or Symbol contains those keywords
is_eq_stock = lambda name, symbol: not any(keyword in name.upper() or keyword in symbol.upper() for keyword in non_eq_keywords)
df_eq = df[df.apply(lambda r: is_eq_stock(r['Stock Name'], r['Symbol']), axis=1)]

# Save the clean list
df_eq.to_csv("nse_only_eq_stocks.csv", index=False)

print(f"Total NSE EQ stocks: {len(df_eq)}")
