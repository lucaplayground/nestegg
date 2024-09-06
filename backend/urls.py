from django.contrib import admin
from django.urls import path, include
from accounts.views import LoginView
from investments.views import HomeView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView, name='login'),  # set the login page as the root page
    path('accounts/', include('accounts.urls')),
    path('home/', HomeView, name='home'),
    path('', include('investments.urls')),
]
