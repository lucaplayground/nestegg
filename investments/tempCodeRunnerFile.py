asset_symbols = ['AAPL', '161005.SZ', 'VT', 'FNZ.NZ', 'BIL']

for symbol in asset_symbols:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    print(f"Data for {symbol}: {info}")