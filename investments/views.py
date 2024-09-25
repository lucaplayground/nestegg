from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Asset, PortfolioAsset, Portfolio
from . import utils
from . import api
from .forms import PortfolioForm
from django.db.models import Q
import logging


# Set up logging
logger = logging.getLogger(__name__)


# Dashboard view
@login_required
def DashboardView(request):
    return render(request, 'investments/dashboard.html')


# List all portfolios
@login_required
def list_portfolios(request):
    portfolios = Portfolio.objects.filter(user=request.user).order_by('-created_at').prefetch_related('portfolio_assets__asset')
    for portfolio in portfolios:
        portfolio.portfolio_value = utils.get_portfolio_value(portfolio)
    return render(request, 'investments/portfolios.html', {'portfolios': portfolios})


# Add a portfolio
@login_required
def add_portfolio(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            messages.success(request, 'Portfolio created successfully.')
            return redirect('list_portfolios')
    else:
        form = PortfolioForm()
    return render(request, 'investments/add_portfolio.html', {'form': form})


# Portfolio detail view
@login_required
@require_http_methods(['GET', 'POST', 'DELETE'])
def portfolio_detail(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio).select_related('asset')

    if request.method == 'POST':
        data = json.loads(request.body)
        assets_to_update = data.get('assets', [])

        try:
            for asset_data in assets_to_update:
                portfolio_asset = portfolio_assets.get(id=asset_data['id'])
                new_position = int(asset_data['position'])
                portfolio_asset.position = new_position
                portfolio_asset.save()

            # Update the portfolio value, asset market value, and asset ratios
            updates = utils.refresh_portfolio_data(portfolio)
            return JsonResponse({
                'success': True,
                'portfolio_value': updates['portfolio_value'],
                'updated_assets': updates['assets_updates']
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    if request.method == 'DELETE':
        data = json.loads(request.body)
        assets_to_delete = data.get('assets', [])

        try:
            PortfolioAsset.objects.filter(portfolio=portfolio, id__in=assets_to_delete).delete()

            # Refresh asset data after deletion
            updates = utils.refresh_portfolio_data(portfolio)

            return JsonResponse({
                'success': True,
                'message': 'Assets deleted successfully',
                'portfolio_value': updates['portfolio_value'],
                'updated_assets': updates['assets_updates']
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    # GET request
    portfolio_value = utils.get_portfolio_value(portfolio)

    # Fetch and display assets details
    for portfolio_asset in portfolio_assets:
        portfolio_asset.market_value = portfolio_asset.get_asset_value()
        portfolio_asset.asset_ratio = utils.get_asset_ratio(portfolio_asset)
            
    context = {
        'portfolio': portfolio,
        'portfolio_assets': portfolio_assets,
        'portfolio_value': portfolio_value
    }
    
    return render(request, 'investments/portfolio_detail.html', context)


# Edit a portfolio
@login_required
def edit_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Portfolio updated successfully.')
            return redirect('list_portfolios')
    else:
        form = PortfolioForm(instance=portfolio)
    return render(request, 'investments/edit_portfolio.html', {'form': form, 'portfolio': portfolio})


# Delete a portfolio
@login_required
def delete_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        portfolio.delete()
        return redirect('list_portfolios')  # Redirect to the list of portfolios
    return render(request, 'investments/delete_portfolio.html', {'portfolio': portfolio})


# List all assets in a portfolio
@login_required
def list_portfolio_assets(request, portfolio_id):
    assets = PortfolioAsset.objects.filter(portfolio_id=portfolio_id)  # Fetch all assets in a portfolio
    return render(request, 'investments/portfolio_assets.html', {'assets': assets})


# Asset detail view
@login_required
def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    return render(request, 'investments/asset_detail.html', {'asset': asset})


# Search for assets
@login_required
def search_assets(request):
    query = request.GET.get('query', '').strip()
    portfolio_id = request.GET.get('portfolio_id')
    
    if query:
        assets = Asset.objects.filter(Q(symbol__icontains=query) | Q(name__icontains=query))
        
        if portfolio_id:
            portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
            existing_assets = PortfolioAsset.objects.filter(portfolio=portfolio).values_list('asset__symbol', flat=True)
            assets = assets.exclude(symbol__in=existing_assets)
        
        results = [{'symbol': asset.symbol, 'name': asset.name} for asset in assets]
        
        if not results:
            # Try to fetch from API if not found in database
            api_asset = api.get_asset_data(query)
            if api_asset:
                results.append({'symbol': api_asset.symbol, 'name': api_asset.name})
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})


# Add an asset to a portfolio
@login_required
def add_asset(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        assets_to_add = request.POST.getlist('assets[]')
        positions = request.POST.getlist('positions[]')
        
        added_assets = []
        for symbol, position in zip(assets_to_add, positions):
            if not PortfolioAsset.objects.filter(portfolio=portfolio, asset__symbol=symbol).exists():
                portfolio_asset = utils.add_asset_to_portfolio(portfolio, symbol, position)
                if portfolio_asset:
                    added_assets.append(symbol)
        
        if added_assets:
            return JsonResponse({'success': True, 'added_assets': added_assets})
        else:
            return JsonResponse({'success': False, 'error': 'No assets were added'})
    
    # Get all assets and mark those already in the portfolio
    all_assets = Asset.objects.all().order_by('symbol')
    portfolio_asset_symbols = set(PortfolioAsset.objects.filter(portfolio=portfolio).values_list('asset__symbol', flat=True))
    
    for asset in all_assets:
        asset.in_portfolio = asset.symbol in portfolio_asset_symbols
    
    context = {
        'portfolio': portfolio,
        'all_assets': all_assets,
    }

    return render(request, 'investments/add_asset.html', {'portfolio': portfolio})


# Delete an asset from a portfolio
@login_required
def delete_portfolio_asset(request, portfolio_asset_id):
    portfolio_asset = get_object_or_404(PortfolioAsset, id=portfolio_asset_id, portfolio__user=request.user)
    if request.method == 'POST':
        portfolio_asset.delete()
        return JsonResponse({'success': True})
    return render(request, 'investments/delete_portfolio_asset.html', {'portfolio_asset': portfolio_asset})