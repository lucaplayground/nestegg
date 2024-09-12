from django.urls import path
from .views import DashboardView, list_portfolios, add_portfolio, portfolio_detail, update_portfolio, delete_portfolio, list_portfolio_assets, search_asset, add_asset, update_asset_position, delete_portfolio_asset

urlpatterns = [
    path('dashboard/', DashboardView, name='dashboard'),
    path('portfolios/', list_portfolios, name='list_portfolios'),
    path('add_portfolio/', add_portfolio, name='add_portfolio'),
    path('portfolios/<int:portfolio_id>/', portfolio_detail, name='portfolio_detail'),
    path('portfolios/update/<int:portfolio_id>/', update_portfolio, name='update_portfolio'),
    path('portfolios/delete/<int:portfolio_id>/', delete_portfolio, name='delete_portfolio'),
    path('assets/<int:portfolio_id>/', list_portfolio_assets, name='list_portfolio_assets'),
    path('assets/search/', search_asset, name='search_asset'),
    path('add_asset/<int:portfolio_id>/', add_asset, name='add_asset'),
    path('assets/update/<int:portfolio_asset_id>/', update_asset_position, name='update_asset_position'),
    path('assets/delete/<int:portfolio_id>/', delete_portfolio_asset, name='delete_portfolio_asset'),
]