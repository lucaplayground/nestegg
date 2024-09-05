from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Default fields
    email = models.EmailField(unique=True)
    
    # Custom fields
    
    def __str__(self):
        return self.username