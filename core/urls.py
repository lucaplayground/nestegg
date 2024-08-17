from django.urls import path
from . import views

# Map a URL to index view
urlpatterns = [
    path("", views.index, name="index"),
]