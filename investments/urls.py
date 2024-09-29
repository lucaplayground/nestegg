from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView, name='dashboard'),
    path('portfolios/', views.list_portfolios, name='list_portfolios'),
    path('add_portfolio/', views.add_portfolio, name='add_portfolio'),
    path('portfolios/<int:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('portfolios/edit/<int:portfolio_id>/', views.edit_portfolio, name='edit_portfolio'),
    path('portfolios/delete/<int:portfolio_id>/', views.delete_portfolio, name='delete_portfolio'),
    path('assets/<int:portfolio_id>/', views.list_portfolio_assets, name='list_portfolio_assets'),
    path('assets/search/', views.search_assets, name='search_assets'),
    path('add_assets/<int:portfolio_id>/', views.add_assets, name='add_assets'),
    path('assets/delete/<int:portfolio_id>/', views.delete_portfolio_asset, name='delete_portfolio_asset'),
]