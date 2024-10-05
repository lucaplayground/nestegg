import yfinance as yf
import logging
import requests
from decimal import Decimal
from typing import List, Dict

# This file contains all the API-related functions

# Set up logging
logger = logging.getLogger(__name__)


def get_asset_data(symbols: List[str]) -> Dict[str, Dict]:
    """Fetch data for multiple assets from YFinance in a single call"""
    try:
        tickers = yf.Tickers(' '.join(symbols))
        result = {}

        for symbol in symbols:
            info = tickers.tickers[symbol].info
            latest_price = info.get('currentPrice') or info.get('previousClose')
            result[symbol] = {
                'name': info.get('shortName'),
                'long_name': info.get('longName'),
                'latest_price': latest_price,
                'asset_type': info.get('quoteType'),
                'currency': info.get('currency'),
                'timezone_full_name': info.get('timeZoneFullName'),
                'timezone_short_name': info.get('timeZoneShortName'),
            }
        return result
    
    except Exception as e:
        logger.error(f"Error fetching asset data for symbols {symbols}: {e}")
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
        response = requests.get(f"https://v6.exchangerate-api.com/v6/9d78c05d8ec5f4fa45392e69/latest/{from_currency}")
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
