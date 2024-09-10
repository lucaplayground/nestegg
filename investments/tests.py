from django.test import TestCase
import yfinance as yf


# Create your tests here.
asset_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

for symbol in asset_symbols:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    print(f"Data for {symbol}: {info}")
