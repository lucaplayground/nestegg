from django.db import models
from django.conf import settings
from .utils import fetch_asset_data, convert_currency
from decimal import Decimal
from django.utils import timezone

# This file includes all the models, their fields and methods, and all related calculations


# Create your models here.
class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_total_value(self):
        return sum(portfolio_asset.get_value_in_portfolio_currency() for portfolio_asset in self.portfolio_assets.all())
        
    def get_latest_update(self):
        latest_asset = self.portfolio_assets.order_by('-asset__last_updated').first()
        return latest_asset.asset.last_updated if latest_asset else self.updated_at


class Asset(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)  # e.g., AAPL, GOOGL, etc.
    asset_type = models.CharField(max_length=50)  # e.g., Equity, ETF, etc.
    latest_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')  # e.g., USD, CNY, JPY, etc.
    last_updated = models.DateTimeField(auto_now=True)  # Track when the asset data was last updated

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
    # @classmethod
    # def create_asset(cls, symbol, data):
    #     return cls.objects.create(
    #         symbol=symbol,
    #         name=data['name'],
    #         asset_type=data['asset_type'],
    #         latest_price=data['latest_price'],
    #         currency=data['currency'],
    #         last_updated=timezone.now()
    #     )
    
    # @classmethod
    # def update_price(self, latest_price):
    #     self.latest_price = latest_price
    #     self.last_updated = timezone.now()
    #     self.save()


class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio_assets')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='portfolio_assets')
    position = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # number of shares/units held
    target_ratio = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # target position percentage

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.name}"
    
    def get_asset_value(self):
        asset_value = self.asset.latest_price*self.position
        return Decimal(asset_value)
    
    def get_asset_value_in_target_currency(self):
        asset_value = self.get_asset_value()
        target_currency = self.portfolio.currency
        asset_currency = self.asset.currency
        asset_value_in_target_currency = convert_currency(asset_value, asset_currency, target_currency)
        return Decimal(asset_value_in_target_currency)


class PositionHistory(models.Model):
    portfolio_asset = models.ForeignKey(PortfolioAsset, on_delete=models.CASCADE, related_name='position_history')  # foreign key linking to PortfolioAsset model
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically record when the position was updated
    position = models.DecimalField(max_digits=10, decimal_places=2)  # The position at that time
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the asset at that time

    def __str__(self):
        return f"{self.portfolio_asset} - {self.timestamp}"
