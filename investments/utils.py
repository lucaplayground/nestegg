import yfinance as yf
from .models import Asset


def update_asset_data(symbol):
    # Fetch data from Yahoo Finance
    ticker = yf.Ticker(symbol)
    info = ticker.info

    # Update or create the asset in the database
    asset, created = Asset.objects.update_or_create(
        symbol=symbol,
        defaults={
            'name': info.get('longName', 'Unknown'),  # Default to Unknown if not found
            'asset_type:': info.get('quoteType', 'Unknown')  # Default to Unknown if not found
            'latest_price': info.get('regularMarketPrice',0),  # Default to 0 if not found
            'currency': info.get('currency', 'Unknown')  # Default to Unknown if not found
        }
    )
    return asset
