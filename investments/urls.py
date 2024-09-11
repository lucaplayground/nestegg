from django.urls import path
from .views import HomeView, PortfolioView, search_assets, add_asset, update_position

urlpatterns = [
    path('home/', HomeView, name='home'),
    path('portfolio/', PortfolioView, name='portfolio'),
    path('search_assets/', search_assets, name='search_assets'),
    path('add_asset/<int:portfolio_id>/', add_asset, name='add_asset'),
    path('update_position/<int:portfolio_asset_id>/', update_position, name='update_position'),  # New URL pattern
]