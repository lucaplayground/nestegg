asset_symbols = ['161005.SZ', '3032.HK', 'FNZ.NZ', 'EDV', 'AAPL']

for symbol in asset_symbols:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    print(f"Data for {symbol}: {info}")