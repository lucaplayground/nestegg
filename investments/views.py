from django.shortcuts import render, redirect
import yfinance as yf
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Asset, PortfolioAsset, PositionHistory, Portfolio


# Home view
@login_required
def HomeView(request):
    return render(request, 'investments/home.html')


# List all portfolios
@login_required
def list_portfolios(request):
    portfolios = Portfolio.objects.filter(user=request.user)  # Fetch portfolios for the logged-in user
    return render(request, 'investments/portfolios.html', {'portfolios': portfolios})


# Function to add a portfolio
@login_required
def add_portfolio(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Portfolio.objects.create(user=request.user, name=name)
            return redirect('portfolio')  # Redirect to the portfolio list page
    return render(request, 'investments/add_portfolio.html')


# Portfolio detail view
@login_required
def portfolio_detail(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    return render(request, 'investments/portfolio_detail.html', {'portfolio': portfolio})


# Function to update a portfolio
@login_required
def update_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        portfolio.name = request.POST.get('name', portfolio.name)
        portfolio.save()
        return redirect('portfolio_detail', portfolio_id=portfolio.id)  # Redirect to the portfolio detail page
    return render(request, 'investments/update_portfolio.html', {'portfolio': portfolio})


# Function to delete a portfolio
@login_required
def delete_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        portfolio.delete()
        return redirect('list_portfolios')  # Redirect to the list of portfolios
    return render(request, 'investments/delete_portfolio.html', {'portfolio': portfolio})


# List all assets
@login_required
def list_assets(request):
    assets = Asset.objects.all()  # Fetch all assets
    return render(request, 'investments/list_assets.html', {'assets': assets})


# Asset detail view
@login_required
def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    return render(request, 'investments/asset_detail.html', {'asset': asset})


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


# Function to update the position of an asset
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


# Funciton to delete an asset
@login_required
def delete_asset(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    if request.method == 'POST':
        asset.delete()
        return JsonResponse({'success': True})
    return render(request, 'investments/delete_asset.html', {'asset': asset})