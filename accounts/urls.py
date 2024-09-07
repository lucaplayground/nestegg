from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginView, name='login'),  # set the login page as the root page
    path('register/', views.RegisterView, name='register'),
    path('logout/', views.LogoutView, name='logout'),
    path('about/', views.AboutView, name='about'),
]
