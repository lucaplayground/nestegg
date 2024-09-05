from django.contrib import admin
from django.urls import path, include
from accounts.views import LoginView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView, name='login'),  # set the login page as the root page
    path('accounts/', include('accounts.urls')),
    path('', include('investments.urls')),
]
