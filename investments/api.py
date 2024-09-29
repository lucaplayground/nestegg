import yfinance as yf
import logging
import requests
from decimal import Decimal
from typing import List, Dict

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
        long_name = info.get('longName')
        asset_type = info.get('quoteType')
        currency = info.get('currency')
        
        return {
            'name': name,
            'long_name': long_name,
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
        response = requests.get(f"https://v6.exchangerate-api.com/v6/d96d7e2e9ecde16ce5b70d32/latest/{from_currency}")
        data = response.json()
        if data['result'] == 'success':
            return Decimal(str(data['conversion_rates'][to_currency]))

    except Exception as e:
        logger.error(f"Error fetching exchange rate for {from_currency} to {to_currency}: {e}")
        return None
    

def search_assets(query: str, limit: int = 10) -> List[Dict]:
    """
    Search for assets based on the query, matching shortName, longName, and symbol.
    Support partial matches and limits the number of results for performance.
    """
    try:
        # Use Yahoo Finance search API directly to search for assets
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount={limit}&newsCount=0&enableFuzzyQuery=false&quotesQueryId=tss_match_phrase_query"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()

        if 'quotes' in data:
            results = []
            for quote in data['quotes']:
                results.append({
                    'symbol': quote.get('symbol'),
                    'name': quote.get('shortname') or quote.get('longname'),
                    'exchange': quote.get('exchange'),
                    'asset_type': quote.get('quoteType')
                })
            # print(results)
            return results
        else:
            return []
    
    except Exception as e:
        logger.error(f"Error searching for assets with query '{query}': {e}")
        return []
