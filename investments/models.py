from django.db import models
from django.conf import settings
from .constants import SUPPORTED_CURRENCY
from decimal import Decimal

# This file includes models and their methods


# Create your models here.
class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.CharField(max_length=3, choices=SUPPORTED_CURRENCY, default='USD')

    def __str__(self):
        return self.name


class Asset(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)  # e.g., AAPL, GOOGL, etc.
    asset_type = models.CharField(max_length=50)  # e.g., Equity, ETF, etc.
    latest_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')  # e.g., USD, CNY, JPY, etc.
    updated_at = models.DateTimeField(auto_now=True)  # Track when the asset data was last updated

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio_assets')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='portfolio_assets')
    position = models.PositiveIntegerField()  # number of shares/units held
    # target_ratio = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # target position percentage

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.name}"
    
    def get_asset_value(self):
        asset_value = self.asset.latest_price*self.position
        return Decimal(asset_value)


# class PositionHistory(models.Model):
#     portfolio_asset = models.ForeignKey(PortfolioAsset, on_delete=models.CASCADE, related_name='position_history')  # foreign key linking to PortfolioAsset model
#     timestamp = models.DateTimeField(auto_now_add=True)  # Automatically record when the position was updated
#     position = models.PositiveIntegerField()  # The position at that time
#     price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the asset at that time

#     def __str__(self):
#         return f"{self.portfolio_asset} - {self.timestamp}"


class TotalValueHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='total_value_history')
    timestamp = models.DateTimeField(auto_now_add=True)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        ordering = ['-timestamp']
        # Create an entry once per day
        constraints = [
            models.UniqueConstraint(fields=['user', 'timestamp'], name='unique_user_daily_value')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.date()} - {self.total_value}"