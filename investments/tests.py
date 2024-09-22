from django.test import TestCase
from django.db.models import F
from django.shortcuts import render
import yfinance as yf


# Create your tests here.
# asset_symbols = ['AAPL', '161005.SZ', 'VT', 'FNZ.NZ', 'BIL']

# for symbol in asset_symbols:
#     ticker = yf.Ticker(symbol)
#     info = ticker.info
#     print(f"Data for {symbol}: {info}")


# class PositionHistoryTestCase(TestCase):
# def position_history(request):
#     # Get all position history entries, ordered by the most recent first
#     history = PositionHistory.objects.select_related('portfolio_asset__asset', 'portfolio_asset__portfolio').order_by('-timestamp')

#     # Calculate the change in position
#     history = history.annotate(
#         position_change=F('portfolio_asset__position') - F('position')
#     )

#     context = {
#         'history': history
#     }
#     return render(request, 'position_history.html', context)