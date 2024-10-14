import logging
from decimal import Decimal
from . import api
from .models import Portfolio, PortfolioAsset, Asset, TotalValueHistory
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

# This file contains general utility functions

# Set up logging
logger = logging.getLogger(__name__)


def create_asset(symbol):
    """Fetch API data and create an asset in the database"""
    try:
        asset_data = api.get_asset_data([symbol])
        if asset_data and symbol in asset_data:
            data = asset_data[symbol]
            asset, created = Asset.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': data.get('name') or data.get('long_name', 'Unknown'),
                    'asset_type': data.get('asset_type', 'Unknown'),
                    'latest_price': data.get('latest_price'),
                    'currency': data.get('currency'),
                    'timezone_full_name': data.get('timezone_full_name'),
                    'timezone_short_name': data.get('timezone_short_name')
                }
            )
            # print(f"{asset.symbol} - {asset.asset_type} - {asset.latest_price}")
            logger.info(f"Updated asset: {asset.name} ({asset.symbol})")
            return asset
        else:
            logger.error(f"No data returned for symbol: {symbol}")

    except Exception as e:
        logger.error(f"Error updating asset data for {symbol}: {e}")
        # print(f"Error updating asset data for {symbol}: {e}")  # Print the error for console feedback
        return None


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
    """Calculate the total value of the portfolio in the portfolio currency"""
    cache_key = f'portfolio_value_{portfolio.id}'
    cached_value = cache.get(cache_key)
    if cached_value is not None:
        return cached_value

    portfolio_value = Decimal(0)
    for portfolio_asset in portfolio.portfolio_assets.all():
        asset_converted_value = get_asset_value_in_portfolio_currency(portfolio_asset)
        if asset_converted_value:
            portfolio_value += asset_converted_value
        else:
            logger.error(f"Error converting currency for asset: {portfolio_asset.asset.name} ({portfolio_asset.asset.symbol})")
    
    cache.set(cache_key, portfolio_value, 5)  # Cache for 5 seconds
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
    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio).select_related('asset')
    total_value = sum(asset.position * asset.asset.latest_price for asset in portfolio_assets)
    
    updates = []
    for asset in portfolio_assets:
        market_value = asset.position * asset.asset.latest_price
        asset_ratio = (market_value / total_value) * 100 if total_value else 0
        updates.append({
            'id': asset.id,
            'market_value': float(market_value),
            'asset_ratio': float(asset_ratio)
        })
    
    return {
        'portfolio_value': float(total_value),
        'assets_updates': updates
    }


def convert_currency(amount, from_currency, to_currency):
    """Convert the amount from one currency to another using the exchange rate"""
    if from_currency == to_currency:
        return Decimal(amount)
    
    cache_key = f'exchange_rate_{from_currency}_{to_currency}'
    exchange_rate = cache.get(cache_key)
    
    if exchange_rate is None:
        exchange_rate = api.get_exchange_rate(from_currency, to_currency)
        cache.set(cache_key, exchange_rate, 3600)  # Cache for 1 hour

    return amount * Decimal(str(exchange_rate))


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


def get_asset_value_in_user_currency(portfolio_asset, user):
    """Convert the asset value to the user's currency"""
    asset_value = portfolio_asset.get_asset_value()
    converted_value = convert_currency(asset_value, portfolio_asset.asset.currency, user.default_currency)
    return converted_value


def update_total_value_history(user):
    """Update the total value history for the user"""
    today = timezone.now().date()
    
    with transaction.atomic():
        # Check if an entry already exists for today
        existing_entry = TotalValueHistory.objects.filter(user=user, timestamp__date=today).first()
        
        total_value = get_total_value(user)
        
        if existing_entry:
            # Update the existing entry if the value has changed
            if existing_entry.total_value != total_value:
                existing_entry.total_value = total_value
                existing_entry.save()
        else:
            # Create a new entry if one doesn't exist for today
            TotalValueHistory.objects.create(user=user, total_value=total_value, timestamp=timezone.now())