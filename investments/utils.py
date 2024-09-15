from .api import get_asset_data, get_exchange_rate
import logging
from decimal import Decimal
from django.utils import timezone

# This file contains all the API-related functions and general utility functions

# Set up logging
logger = logging.getLogger(__name__)

# Supported currencies in the system
# SUPPORTED_CURRENCIES = ['USD', 'CNY', 'NZD']


def add_asset_to_portfolio(portfolio, symbol, quantity):
    pass


def update_asset_price(asset):
    """Update the latest price for the asset"""
    try:
        data = get_asset_data(asset.symbol)
        if data:
            asset.latest_price = data['latest_price']
            asset.last_updated = timezone.now()
            asset.save()
            logger.info(f"Updated latest price for asset: {asset.name} ({asset.symbol})")
            return asset
    except Exception as e:
        logger.error(f"Error updating asset data for {asset.symbol}: {e}")
        return None


# 
def get_value_in_portfolio_currency(portfolio_asset):
    value = portfolio_asset.get_value()
    return convert_currency(value, portfolio_asset.asset.currency, portfolio_asset.portfolio.currency)


def convert_currency(amount, from_currency, to_currency):
    """Convert the amount from one currency to another using the exchange rate"""
    if from_currency == to_currency:
        return Decimal(amount)
    exchange_rate = get_exchange_rate(from_currency, to_currency)
    if exchange_rate is None:
        return None
    converted_amount = Decimal(amount)*exchange_rate
    return converted_amount
