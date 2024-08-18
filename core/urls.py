from django.urls import path
from . import views

# Map URLs to views
urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
]