from django.urls import path
from .views import HomeView, list_portfolios, portfolio_detail, update_portfolio, delete_portfolio, search_assets, add_asset, update_position, list_assets, asset_detail

urlpatterns = [
    path('home/', HomeView, name='home'),
    path('portfolios/', list_portfolios, name='list_portfolios'),
    path('portfolios/<int:portfolio_id>/', portfolio_detail, name='portfolio_detail'),
    path('portfolios/update/<int:portfolio_id>/', update_portfolio, name='update_portfolio'),
    path('portfolios/delete/<int:portfolio_id>/', delete_portfolio, name='delete_portfolio'),
    path('assets/<int:portfolio_id>/', list_assets, name='list_assets'),
    path('asset_detail/<int:portfolio_asset_id>/', asset_detail, name='asset_detail'),
    path('search_assets/', search_assets, name='search_assets'),
    path('add_asset/<int:portfolio_id>/', add_asset, name='add_asset'),
    path('assets/update/<int:portfolio_asset_id>/', update_position, name='update_position'),
    path('assets/delete/<int:portfolio_id>/', delete_portfolio, name='delete_portfolio'),
]