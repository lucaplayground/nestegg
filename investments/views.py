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
    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio).select_related('asset').prefetch_related('portfolio')

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
    query = request.GET.get('q', '').strip()
    portfolio_id = request.GET.get('portfolio_id')

    # Return an empty list if the query is too short
    if len(query) < 3:
        return JsonResponse({'results': []})
    
    try:
        results = api.search_assets(query)

        if portfolio_id:
            # Get existing assets in the portfolio
            existing_assets = set(PortfolioAsset.objects.filter(portfolio_id=portfolio_id).values_list('asset__symbol', flat=True))
            
            # Mark existing assets in the results
            for result in results:
                result['exists_in_portfolio'] = result['symbol'] in existing_assets
        
        if not results:
            results = [{'symbol': 'No results found', 'name': '', 'exists_in_portfolio': False}]
        
        return JsonResponse({'results': results})
    except Exception as e:
        logger.error(f"Error in search_assets view: {e}")
        return JsonResponse({'results': [{'symbol': 'Error occurred', 'name': '', 'exists_in_portfolio': False}]}, status=500)


# Add an asset to a portfolio
@login_required
@require_http_methods(["GET", "POST"])
def add_assets(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)

    if request.method == 'GET':
        return render(request, 'investments/add_assets.html', {'portfolio': portfolio})

    elif request.method == 'POST':
        try: 
            data = json.loads(request.body)
            assets = data.get('assets', [])
            # print(assets)
            logger.info(f"Received request to add assets: {assets}")  # Log the request

            added_assets = []
            existing_assets = []

            for asset_data in assets:
                symbol = asset_data.get('symbol')
                quantity = asset_data.get('quantity')
                
                if not symbol or not quantity:
                    continue

                # Check if the asset already exists in the portfolio
                existing_portfolio_asset = PortfolioAsset.objects.filter(portfolio=portfolio, asset__symbol=symbol).first()

                if existing_portfolio_asset:
                    existing_assets.append({
                        'symbol': symbol,
                        'name': existing_portfolio_asset.asset.name,
                        'current_quantity': existing_portfolio_asset.position
                    })
                    continue

                # Create or update the asset
                asset = utils.create_asset(symbol)
                print(asset)
                if not asset:
                    logger.warning(f"Failed to create asset for symbol: {symbol}")
                    continue

                # Add the asset to the portfolio
                portfolio_asset = PortfolioAsset.objects.create(
                    portfolio=portfolio,
                    asset=asset,
                    position=quantity
                )

                added_assets.append({
                    'symbol': symbol,
                    'name': asset.name,
                    'quantity': quantity
                })
                logger.info(f"Added asset to portfolio: {symbol}")

            logger.info(f"Successfully processed assets. Added: {len(added_assets)}, Already existing: {len(existing_assets)}")
            return JsonResponse({
                'success': True, 
                'message': 'Assets processed successfully',
                'added_assets': added_assets,
                'existing_assets': existing_assets
            })
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'success': False, 'message': 'Invalid JSON in request body'}, status=400)
        
        except Exception as e:
            logger.error(f"Error adding assets to portfolio {portfolio_id}: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


# Delete an asset from a portfolio
@login_required
def delete_portfolio_asset(request, portfolio_asset_id):
    portfolio_asset = get_object_or_404(PortfolioAsset, id=portfolio_asset_id, portfolio__user=request.user)
    if request.method == 'POST':
        portfolio_asset.delete()
        return JsonResponse({'success': True})
    return render(request, 'investments/delete_portfolio_asset.html', {'portfolio_asset': portfolio_asset})