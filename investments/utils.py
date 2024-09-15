import logging
from decimal import Decimal
from django.utils import timezone
from .api import get_asset_data, get_exchange_rate
from .models import Portfolio, PortfolioAsset, Asset

# This file contains general utility functions

# Set up logging
logger = logging.getLogger(__name__)


def create_asset(symbol):
    """Fetch API data and create an asset in the database"""
    try:
        asset_data = get_asset_data(symbol)
        if asset_data:
            asset, created = Asset.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': asset_data['name'],
                    'asset_type': asset_data['asset_type'],
                    'latest_price': asset_data['latest_price'],
                    'currency': asset_data['currency'],
                    'updated_at': timezone.now()
                }
            )

        logger.info(f"Updated asset: {asset.name} ({asset.symbol})")
        return asset

    except Exception as e:
        logger.error(f"Error updating asset data for {symbol}: {e}")
        # print(f"Error updating asset data for {symbol}: {e}")  # Print the error for console feedback
        return None


def update_asset_price(asset):
    """Update the latest price for the asset"""
    try:
        data = get_asset_data(asset.symbol)
        if data:
            asset.latest_price = data['latest_price']
            asset.updated_at = timezone.now()
            asset.save()
            logger.info(f"Updated latest price for asset: {asset.name} ({asset.symbol})")
            return asset
    except Exception as e:
        logger.error(f"Error updating asset data for {asset.symbol}: {e}")
        return None


def add_asset_to_portfolio(portfolio, symbol, quantity):
    """Add an asset to the portfolio"""
    try:
        asset_data = get_asset_data(symbol)
        if asset_data:
            asset, _ = Asset.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': asset_data['name'],
                    'asset_type': asset_data['asset_type'],
                    'latest_price': asset_data['latest_price'],
                    'currency': asset_data['currency'],
                }
            )
            portfolio_asset, created = PortfolioAsset.objects.get_or_create(
                portfolio=portfolio,
                asset=asset,
                defaults={'position': Decimal(quantity)}
            )
            if not created:
                portfolio_asset.position += Decimal(quantity)
                portfolio_asset.save()
            return portfolio_asset
    except Exception as e:
        logger.error(f"Error adding asset {symbol} to portfolio {portfolio.name}: {e}")
        return None


def get_portfolio_total_value(portfolio):
    total_value = Decimal(0)
    for portfolio_asset in portfolio.portfolio_assets.all():
        asset_value = portfolio_asset.get_asset_value()
        converted_value = convert_currency(asset_value, portfolio_asset.asset.currency, portfolio_asset.portfolio.currency)
        if converted_value:
            total_value += converted_value
        else:
            logger.error(f"Error converting currency for asset: {portfolio_asset.asset.name} ({portfolio_asset.asset.symbol})")
        return total_value


def convert_currency(amount, from_currency, to_currency):
    """Convert the amount from one currency to another using the exchange rate"""
    if from_currency == to_currency:
        return Decimal(amount)
    exchange_rate = get_exchange_rate(from_currency, to_currency)
    if exchange_rate is None:
        return None
    converted_amount = Decimal(amount)*exchange_rate
    return converted_amount



