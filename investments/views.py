from django.shortcuts import render
import yfinance as yf
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Asset, PortfolioAsset, PositionHistory, Portfolio


# Home view
def HomeView(request):
    return render(request, 'investments/home.html')


# Portfolio view
def PortfolioView(request):
    return render(request, 'investments/portfolio.html')


# Function to search for assets
def search_assets(request):
    query = request.GET.get('query','')
    if query:
        # Fetch data from Yahoo Finance
        ticker = yf.Ticker(query)
        try:
            info = ticker.info
            asset_data = {
                'name': info.get('longName', 'Unknown'),
                'symbol': info.get('symbol', 'Unknown'),
                'asset_type': info.get('quoteType', 'Unknown'),
                'latest_price': info.get('regularMarketPrice', 0),
                'currency': info.get('currency', 'Unknown')
            }
            return JsonResponse([asset_data])
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse([], safe=False)


# Function to add an asset to a portfolio
@login_required
def add_asset(request, portfolio_id):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        position = request.POST.get('position', 0)

        # Fetch the asset
        ticker = yf.Ticker(symbol)
        info = ticker.info
        asset, created = Asset.objects.update_or_create(
            symbol=symbol,
            defaults={
                'name': info.get('longName', 'Unknown'),
                'asset_type': info.get('quoteType', 'Unknown'),
                'latest_price': info.get('regularMarketPrice', 0),
                'currency': info.get('currency', 'Unknown'),
                'last_updated': timezone.now()
            }
        )

        # Add to PortfolioAsset
        portfolio = get_object_or_404(Portfolio, id=portfolio_id)
        portfolio_asset = PortfolioAsset.objects.create(
            portfolio=portfolio,
            asset=asset,
            position=position
        )

        # Create PositionHistory entry
        PositionHistory.objects.create(
            portfolio_asset=portfolio_asset,
            position=position,
            price_at_time=asset.latest_price
        )

        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def update_position(request, portfolio_asset_id):
    if request.method == 'POST':
        new_position = request.POST.get('position', 0)

        # Fetch the PortfolioAsset instance
        portfolio_asset = get_object_or_404(PortfolioAsset, id=portfolio_asset_id)

        # Update the position
        portfolio_asset.position = new_position
        portfolio_asset.save()

        # Create a PositionHistory entry
        PositionHistory.objects.create(
            portfolio_asset=portfolio_asset,
            position=new_position,
            price_at_time=portfolio_asset.asset.latest_price
        )

        return JsonResponse({'success': True, 'new_position': new_position})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
