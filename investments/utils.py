import yfinance as yf
import logging
from .models import Asset


# Set up logging
logger = logging.getLogger(__name__)


def update_asset_data(symbol):
    try:
        # Fetch data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Check if the data is available
        if 'longName' not in info or 'regularMarketPrice' not in info:
            logger.warning(f"Data not found for symbol: {symbol}")
            return None

        # Update or create the asset in the database
        asset, created = Asset.objects.update_or_create(
            symbol=symbol,
            defaults={
                'name': info.get('longName', 'Unknown'),  # Default to Unknown if not found
                'asset_type': info.get('quoteType', 'Unknown'),  # Default to Unknown if not found
                'latest_price': info.get('regularMarketPrice', 0),  # Default to 0 if not found
                'currency': info.get('currency', 'Unknown')  # Default to Unknown if not found
            }
        )
        logger.info(f"Updated asset: {asset.name} ({asset.symbol})")
        return asset

    except Exception as e:
        logger.error(f"Error updating asset data for {symbol}:{e}")
        return None
