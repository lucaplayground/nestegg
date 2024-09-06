from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Default fields
    email = models.EmailField(unique=True)

    # Custom fields
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('CNY', 'Chinese Yuan'),
        ('NZD', 'New Zealand Dollar'),
    ]

    default_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text="Currency used to display the total amount of investments."
    )
    
    def __str__(self):
        return self.username