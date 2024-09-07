from django.urls import path
from .views import HomeView, PortfolioView

urlpatterns = [
    path('home/', HomeView, name='home'),
    path('portfolio/', PortfolioView, name='portfolio'),
]