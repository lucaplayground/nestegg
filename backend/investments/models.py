from django.db import models
from django.conf import settings
from common.constants import CURRENCY_CHOICES


class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"
    

class Asset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='assets')
    symbol = models.CharField(max_length=10)
    position = models.IntegerField()  # Number of units/shares held
    latest_price = models.DecimalField(max_digits=10, decimal_places=2)
    market_value = models.DecimalField(max_digits=15, decimal_places=2)
    pl_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage change in position value
    rebalance_percentage = models.DecimalField(max_digits=5, decimal_places=2)   # Desired portfolio allocation
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol} in {self.portfolio.name}"
    
    def update_price(self, price):
        """ Update the latest price of the asset, called from an external service """
        self.latest_price = price
        self.save()