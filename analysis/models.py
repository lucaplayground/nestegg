from django.db import models
from core.models import Portfolio  # Import Portfolio model from core app


# Create your models here.
class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    currency_code = models.CharField(max_length=10, choices=[
        ('USD', 'US Dollar'),
        ('NZD', 'New Zealand Dollar'),
        ('AUD', 'Australian Dollar'),
        ('JPY', 'Japanese Yen'),
        ('CNY', 'Chinese Yuan'),
        ('GBP', 'British Pound'),
        ('EUR', 'Euro'),
        ('CAD', 'Canadian Dollar'),
        ('SGD', 'Singapore Dollar'),
    ])

    def __str__(self):
        return self.name


class PortfolioAsset(models.Model):
    portfolio_asset_id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    position = models.DecimalField(max_digits=10, decimal_places=2)
    cost_basis = models.DecimalField(max_digits=15, decimal_places=2)
    targeted_ratio = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.portfolio.portfolio_name} - {self.asset.name}"