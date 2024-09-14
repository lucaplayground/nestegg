import yfinance as yf
import logging
from .models import Asset
from django.utils import timezone
import requests
from decimal import Decimal


# Set up logging
logger = logging.getLogger(__name__)


def create_asset(symbol):
    """Fetch all data for the asset and create or update it in the database"""
    try:
        # Fetch data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Log the raw info for debugging
        logger.info(f"Raw data for {symbol}: {info}")
        # print(f"Raw data for {symbol}: {info}")  # Print raw data to debug

        # Fetch data from YFinance
        name = info.get('shortName')
        latest_price = info.get('currentPrice')
        asset_type = info.get('quoteType')
        currency = info.get('currency')

        # print(name)
        # print(latest_price)

        # Check if any fields are missing
        if not name or not latest_price:
            logger.warning(f"Data not found for symbol: {symbol}")
            # print(f"Data not found for symbol: {symbol}")
            return None

        # Update or create the asset in the database
        asset, created = Asset.objects.update_or_create(
            symbol=symbol,
            defaults={
                'name': name or 'Unknown',  # Default to 'Unknown' if not found
                'asset_type': asset_type or 'Unknown',  # Default to 'Unknown' if not found
                'latest_price': latest_price or 0,  # Default to 0 if not found
                'currency': currency or 'Unknown',  # Default to 'Unknown' if not found
                'last_updated': timezone.now()
            }
        )
        logger.info(f"Updated asset: {asset.name} ({asset.symbol})")
        return asset

    except Exception as e:
        logger.error(f"Error updating asset data for {symbol}: {e}")
        # print(f"Error updating asset data for {symbol}: {e}")  # Print the error for console feedback
        return None
    

def update_asset(symbol):
    """Fetch only the latest price for the asset and update it in the database."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Log the raw info for debugging
        logger.info(f"Raw data for {symbol}: {info}")

        # Fetch only the latest price
        latest_price = info.get('currentPrice', 0)

        # Check if the latest price is available
        if latest_price is None:
            logger.warning(f"Latest price not found for symbol: {symbol}")
            return None
        
        # Update the asset's latest price in the database
        asset = Asset.objects.filter(symbol=symbol).first()
        if asset:
            asset.latest_price = latest_price
            asset.last_updated = timezone.now()
            asset.save()
            logger.info(f"Updated latest price for asset: {asset.name} ({asset.symbol})")
            return asset
        
    except Exception as e:
        logger.error(f"Error updating asset data for {symbol}: {e}")
        return None
    

def get_exchange_rate(from_currency, to_currency):
    """Fetch the exchange rate for the two currencies"""
    try:
        response = requests.get(f"https://v6.exchangerate-api.com/v6/1ce094a26ea0970bcc613c49/latest/{from_currency}")
        data = response.json()
        if data['result'] == 'success':
            return Decimal(str(data['conversion_rates'][to_currency]))

    except Exception as e:
        logger.error(f"Error fetching exchange rate for {from_currency} to {to_currency}: {e}")
        return None
    

def convert_currency(amount, from_currency, to_currency):
    """Convert the amount from one currency to another using the exchange rate"""
    if from_currency == to_currency:
        return Decimal(amount)
    exchange_rate = get_exchange_rate(from_currency, to_currency)
    if exchange_rate is None:
        return None
    converted_amount = Decimal(amount)*exchange_rate
    return converted_amount
