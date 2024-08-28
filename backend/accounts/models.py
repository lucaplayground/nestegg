from django.db import models
from django.contrib.auth.models import AbstractUser
from common.constants import CURRENCY_CHOICES


# extend the default Django User model
class CustomUser(AbstractUser):
    default_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')