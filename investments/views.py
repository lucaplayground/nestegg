from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Count, F, FloatField, DecimalField, ExpressionWrapper, Prefetch, Case, When, Value, CharField
from django.db.models.functions import TruncDate, Cast
from django.core.serializers.json import DjangoJSONEncoder
from django.core.cache import cache
from .models import Asset, PortfolioAsset, Portfolio, TotalValueHistory
from .forms import PortfolioForm
from .constants import TIMEZONE_TO_REGION
from . import utils
from . import api
import logging
import json
from decimal import Decimal, InvalidOperation
from datetime import date


# Set up logging
logger = logging.getLogger(__name__)


# Custom JSON encoder to handle Decimal and date
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)


# Dashboard view
@login_required
def dashboard(request):
    user = request.user
    top_assets = get_top_assets(user)
    context = {
        'total_value': get_total_value(user),
        'portfolio_count': Portfolio.objects.filter(user=user).count(),
        'top_assets': top_assets,
    }
    # print("Top assets in dashboard view:", top_assets)  # Debug print
    return render(request, 'investments/dashboard.html', context)


def get_total_value(user):
    cache_key = f'user_{user.id}_total_value'
    total_value = cache.get(cache_key)
    if total_value is None:
        portfolio_assets = PortfolioAsset.objects.filter(portfolio__user=user).select_related('asset')
        total_value = sum(
            utils.convert_currency(
                asset.position * asset.asset.latest_price,
                asset.asset.currency,
                user.default_currency
            )
            for asset in portfolio_assets
        )
        cache.set(cache_key, total_value, 300)  # Cache for 5 minutes
    return total_value


def get_top_assets(user):
    cache_key = f'user_{user.id}_top_assets'
    top_assets = cache.get(cache_key)
    if top_assets is None:
        portfolio_assets = PortfolioAsset.objects.filter(portfolio__user=user).select_related('asset')
        asset_values = {}
        for asset in portfolio_assets:
            value = utils.convert_currency(
                asset.position * asset.asset.latest_price,
                asset.asset.currency,
                user.default_currency
            )
            if asset.asset.symbol in asset_values:
                asset_values[asset.asset.symbol]['total_value'] += value
            else:
                asset_values[asset.asset.symbol] = {
                    'asset__symbol': asset.asset.symbol,
                    'asset__name': asset.asset.name,
                    'total_value': value
                }
        top_assets = sorted(asset_values.values(), key=lambda x: x['total_value'], reverse=True)[:5]
        cache.set(cache_key, top_assets, 300)  # Cache for 5 minutes
    
    # Convert Decimal to float for JSON serialization
    for asset in top_assets:
        asset['total_value'] = float(asset['total_value'])
    
    return top_assets


def value_history_data(request):
    user = request.user
    cache_key = f'user_{user.id}_value_history'
    data = cache.get(cache_key)
    if data is None:
        history = TotalValueHistory.objects.filter(user=user).order_by('timestamp')
        data = [
            {
                'timestamp': entry.timestamp,
                'total_value': float(entry.total_value)  # Assuming total_value is already in user's default currency
            }
            for entry in history
        ]
        cache.set(cache_key, data, 3600)  # Cache for 1 hour
    return JsonResponse(data, safe=False)


def geographic_distribution_data(request):
    user = request.user
    cache_key = f'user_{user.id}_geographic_distribution'
    data = cache.get(cache_key)

    if data is None:
        try:
            portfolio_assets = PortfolioAsset.objects.filter(portfolio__user=user).select_related('asset')
            
            geographic_distribution = {}
            for portfolio_asset in portfolio_assets:
                region = next((region for tz, region in TIMEZONE_TO_REGION.items() 
                               if portfolio_asset.asset.timezone_full_name == tz), 'Other')
                
                asset_value = utils.convert_currency(
                    portfolio_asset.position * portfolio_asset.asset.latest_price,
                    portfolio_asset.asset.currency,
                    user.default_currency
                )
                geographic_distribution[region] = geographic_distribution.get(region, Decimal(0)) + asset_value

            data = [
                {'region': region, 'total_value': float(value)}
                for region, value in geographic_distribution.items()
            ]
            data.sort(key=lambda x: x['total_value'], reverse=True)

            cache.set(cache_key, data, 3600)  # Cache for 1 hour
        except Exception as e:
            logger.error(f"Error calculating geographic distribution for user {user.id}: {str(e)}")
            data = []

    return JsonResponse(data, safe=False)


def asset_types_data(request):
    user = request.user
    cache_key = f'user_{user.id}_asset_types'
    data = cache.get(cache_key)

    if data is None:
        try:
            asset_types = PortfolioAsset.objects.filter(portfolio__user=user)\
                .select_related('asset')\
                .annotate(
                    asset_value=ExpressionWrapper(
                        F('position') * F('asset__latest_price'),
                        output_field=DecimalField(max_digits=19, decimal_places=4)
                    ),
                    category=Case(
                        When(asset__asset_type__in=['STOCK', 'EQUITY'], then=Value('Aggressive')),
                        default=Value('Passive'),
                        output_field=CharField()
                    )
                )\
                .values('category', 'asset_value', 'asset__currency')

            logger.debug(f"Raw asset types query result: {list(asset_types)}")

            processed_data = {'Aggressive': Decimal('0'), 'Passive': Decimal('0')}
            for item in asset_types:
                category = item['category']
                asset_currency = item['asset__currency']
                try:
                    asset_value = Decimal(item['asset_value'] or 0)
                    converted_value = utils.convert_currency(
                        asset_value,
                        asset_currency,
                        user.default_currency
                    )
                    processed_data[category] += converted_value
                except (InvalidOperation, TypeError) as e:
                    logger.error(f"Error processing asset value: {e}")
                    logger.error(f"Problematic item: {item}")

            data = [
                {'category': category, 'total_value': float(total_value)}
                for category, total_value in processed_data.items()
            ]

            logger.debug(f"Processed asset types data: {data}")

            cache.set(cache_key, data, 3600)  # Cache for 1 hour
        except Exception as e:
            logger.error(f"Error calculating asset types for user {user.id}: {str(e)}")
            logger.exception("Full traceback:")
            data = []

    return JsonResponse(data, safe=False)


# List all portfolios
@login_required
def list_portfolios(request):
    cache_key = f'user_{request.user.id}_portfolios'
    portfolios = cache.get(cache_key)

    if portfolios is None:
        portfolios = list(Portfolio.objects.filter(user=request.user)
            .prefetch_related('portfolio_assets__asset'))
        
        # Update portfolio information
        for portfolio in portfolios:
            portfolio.asset_count = portfolio.portfolio_assets.count()
            portfolio.portfolio_value = utils.get_portfolio_value(portfolio)

        cache.set(cache_key, portfolios, 300)  # Cache for 5 minutes
    else:
        # Refresh data for cached portfolios
        for portfolio in portfolios:
            try:
                portfolio.refresh_from_db()
                portfolio.asset_count = portfolio.portfolio_assets.count()
                portfolio.portfolio_value = utils.get_portfolio_value(portfolio)
            except Portfolio.DoesNotExist:
                # Portfolio was deleted, so we don't include it
                portfolios.remove(portfolio)

        # Update the cache with refreshed data
        cache.set(cache_key, portfolios, 300)

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
            # Invalidate the cache
            cache_key = f'user_{request.user.id}_portfolios'
            cache.delete(cache_key)
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

    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio)\
        .select_related('asset')\
        .annotate(
            market_value=ExpressionWrapper(
                F('position') * F('asset__latest_price'),
                output_field=DecimalField(max_digits=19, decimal_places=2)
            )
        )

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

            # Update the total value history
            utils.update_total_value_history(request.user)
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
    portfolio_value = portfolio_assets.aggregate(
        total_value=Sum('market_value')
    )['total_value'] or 0

    # Fetch and display assets details
    for asset in portfolio_assets:
        asset.asset_ratio = (asset.market_value / portfolio_value) * 100 if portfolio_value else 0
            
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
        
        # Invalidate the cache
        cache_key = f'user_{request.user.id}_portfolios'
        cache.delete(cache_key)
        
        messages.success(request, 'Portfolio deleted successfully.')
        return redirect('list_portfolios')
    
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

    print(f"Searching for: {query}")  # Debug print

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
        print(f"Error in search_assets: {e}")  # Debug print
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

            # Update the total value history
            utils.update_total_value_history(request.user)

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