from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView, name='home'),
    path('login/', views.LoginView, name='login'),
    path('register/', views.RegisterView, name='register'),
    path('logout/', views.LogoutView, name='logout'),
    path('about/', views.AboutView, name='about'),
    path('profile/', views.profile, name='profile'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
]
