from django.contrib import admin
from .models import Asset, PortfolioAsset


# Register your models here.
admin.site.register(Asset)
admin.site.register(PortfolioAsset)