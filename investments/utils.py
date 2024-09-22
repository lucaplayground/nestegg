import logging
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from . import api
from .models import Portfolio, PortfolioAsset, Asset, TotalValueHistory

# This file contains general utility functions

# Set up logging
logger = logging.getLogger(__name__)


def create_asset(symbol):
    """Fetch API data and create an asset in the database"""
    try:
        asset_data = api.get_asset_data(symbol)
        if asset_data:
            asset, created = Asset.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': asset_data['name'],
                    'asset_type': asset_data['asset_type'],
                    'latest_price': asset_data['latest_price'],
                    'currency': asset_data['currency'],
                    # 'updated_at': timezone.now()
                }
            )

        logger.info(f"Updated asset: {asset.name} ({asset.symbol})")
        return asset

    except Exception as e:
        logger.error(f"Error updating asset data for {symbol}: {e}")
        # print(f"Error updating asset data for {symbol}: {e}")  # Print the error for console feedback
        return None


# def update_asset_price(asset):
#     """Update the latest price for the asset"""
#     try:
#         data = get_asset_data(asset.symbol)
#         if data:
#             asset.latest_price = data['latest_price']
#             asset.updated_at = timezone.now()
#             asset.save()
#             logger.info(f"Updated latest price for asset: {asset.name} ({asset.symbol})")
#             return asset
#     except Exception as e:
#         logger.error(f"Error updating asset data for {asset.symbol}: {e}")
#         return None


def add_asset_to_portfolio(portfolio, symbol, quantity):
    """Add an asset to the portfolio"""
    try:
        asset_data = api.get_asset_data(symbol)
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


def get_asset_value_in_portfolio_currency(portfolio_asset):
    """Convert the asset value to the portfolio currency"""
    asset_value = portfolio_asset.get_asset_value()
    converted_value = convert_currency(asset_value, portfolio_asset.asset.currency, portfolio_asset.portfolio.currency)
    return converted_value


def get_portfolio_value(portfolio):
    """Sum up asset values in the portfolio"""
    portfolio_value = Decimal(0)
    for portfolio_asset in portfolio.portfolio_assets.all():
        asset_converted_value = get_asset_value_in_portfolio_currency(portfolio_asset)
        if asset_converted_value:
            portfolio_value += asset_converted_value
        else:
            logger.error(f"Error converting currency for asset: {portfolio_asset.asset.name} ({portfolio_asset.asset.symbol})")
    return portfolio_value


def get_asset_ratio(portfolio_asset):
    """Calculate the asset ratio in the portfolio"""
    portfolio_value = get_portfolio_value(portfolio_asset.portfolio)
    asset_converted_value = get_asset_value_in_portfolio_currency(portfolio_asset)
    if portfolio_value == 0:
        return Decimal(0)
    asset_ratio = (asset_converted_value/portfolio_value)*Decimal(100)
    return asset_ratio


def refresh_portfolio_data(portfolio):
    """Refresh asset values, asset ratios, and total value for the portfolio"""
    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio).select_related('asset')
    portfolio_value = get_portfolio_value(portfolio)
    
    assets_updates = []
    for portfolio_asset in portfolio_assets:
        market_value = portfolio_asset.get_asset_value()
        asset_ratio = get_asset_ratio(portfolio_asset)
        assets_updates.append({
            'id': portfolio_asset.id,
            'market_value': float(market_value),  # Convert Decimal to float
            'asset_ratio': float(asset_ratio)  # Convert Decimal to float
        })
    
    return {
        'portfolio_value': float(portfolio_value),  # Convert Decimal to float
        'assets_updates': assets_updates
    }


def convert_currency(amount, from_currency, to_currency):
    """Convert the amount from one currency to another using the exchange rate"""
    if from_currency == to_currency:
        return Decimal(amount)
    exchange_rate = api.get_exchange_rate(from_currency, to_currency)
    if exchange_rate is None:
        return None
    converted_amount = Decimal(amount)*exchange_rate
    return converted_amount


def get_total_value(user):
    """Get the total value of all portfolios for the user in the user's currency"""
    total_value = Decimal(0)
    for portfolio in Portfolio.objects.filter(user=user):
        portfolio_value = get_portfolio_value(portfolio)
        converted_value = convert_currency(portfolio_value, portfolio.currency, user.default_currency)
        if converted_value is not None:
            total_value += converted_value
        else:
            logger.error(f"Error converting currency for portfolio: {portfolio.name}")
    return total_value
