from django import forms
from .models import Portfolio


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }