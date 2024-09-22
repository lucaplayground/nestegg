import yfinance as yf
import logging
import requests
from decimal import Decimal

# This file contains all the API-related functions

# Set up logging
logger = logging.getLogger(__name__)


def get_asset_data(symbol):
    """Fetch all data for an asset from YFinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Log the raw info for debugging
        logger.info(f"Raw data for {symbol}: {info}")
        # print(f"Raw data for {symbol}: {info}")  # Print raw data to debug

        # Fetch data from YFinance
        latest_price = info.get('currentPrice')
        # If current price is not available, use the previous close price
        if not latest_price:
            latest_price = info.get('previousClose')
        
        name = info.get('shortName')
        asset_type = info.get('quoteType')
        currency = info.get('currency')
        
        return {
            'name': name,
            'latest_price': latest_price,
            'asset_type': asset_type,
            'currency': currency
        }
    
    except Exception as e:
        logger.error(f"Error fetching asset data for {symbol}: {e}")
        return None
    

def get_asset_price(symbol):
    """Fetch the latest price for an asset from YFinance"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        latest_price = data['Close'].iloc[-1]
        return Decimal(str(latest_price))
    
    except Exception as e:
        logger.error(f"Error fetching latest price for {symbol}: {e}")
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