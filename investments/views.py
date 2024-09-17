from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Asset, PortfolioAsset, PositionHistory, Portfolio
from .utils import get_portfolio_total_value, get_asset_data, create_asset, add_asset_to_portfolio, update_asset_price
from .forms import PortfolioForm


# Dashboard view
@login_required
def DashboardView(request):
    return render(request, 'investments/dashboard.html')


# List all portfolios
@login_required
def list_portfolios(request):
    portfolios = Portfolio.objects.filter(user=request.user).order_by('-created_at').prefetch_related('portfolio_assets__asset')
    for portfolio in portfolios:
        portfolio.total_value = get_portfolio_total_value(portfolio)
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
def portfolio_detail(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    portfolio_assets = PortfolioAsset.objects.filter(portfolio=portfolio).select_related('asset')

    total_value = get_portfolio_total_value(portfolio)

    for asset in portfolio_assets:
        asset.value = asset.get_asset_value()
        asset.percentage = (asset.market_value / total_value) * 100 if total_value else 0
    
    context = {
        'portfolio': portfolio,
        'portfolio_assets': portfolio_assets,
        'total_value': total_value
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
def search_asset(request):
    query = request.GET.get('query', '').strip()
    if query:
        assets = Asset.objects.filter(
            Q(symbol__icontains=query) | Q(name__icontains=query)
        )[:10]  # Limit to 10 results for performance

        results = [
            {
                'id': asset.symbol,
                'text': f"{asset.symbol} - {asset.name}"
            } for asset in assets
        ]

        # If no results found in the database, try to fetch from the API
        if not results:
            api_asset = create_asset(query)
            if api_asset:
                results.append({
                    'id': api_asset.symbol,
                    'text': f"{api_asset.symbol} - {api_asset.name}"
                })

        return JsonResponse({'results': results})
    return JsonResponse({'results': []})


# Add an asset to a portfolio
@login_required
def add_asset(request, portfolio_id):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        position = request.POST.get('position', 0)
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)

        # Call utility function to add the asset to the porffolio
        portfolio_asset = add_asset_to_portfolio(portfolio, symbol, position)

        if portfolio_asset:
            # Create a PositionHistory entry
            PositionHistory.objects.create(
                portfolio_asset=portfolio_asset,
                position=position,
                price_at_time=portfolio_asset.asset.latest_price
            )
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


# Update the position of an asset
@login_required
def update_asset_position(request, portfolio_asset_id):
    if request.method == 'POST':
        new_position = request.POST.get('position', 0)

        # Fetch the PortfolioAsset instance
        portfolio_asset = get_object_or_404(PortfolioAsset, id=portfolio_asset_id, portfolio__user=request.user)

        # Update the position
        portfolio_asset.position = new_position
        portfolio_asset.save()
        # Update the latest price for the asset
        update_asset_price(portfolio_asset.asset)

        # Create a PositionHistory entry
        PositionHistory.objects.create(
            portfolio_asset=portfolio_asset,
            position=new_position,
            price_at_time=portfolio_asset.asset.latest_price
        )

        return JsonResponse({'success': True, 'new_position': new_position})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# Delete an asset from a portfolio
@login_required
def delete_portfolio_asset(request, portfolio_asset_id):
    portfolio_asset = get_object_or_404(PortfolioAsset, id=portfolio_asset_id, portfolio_user=request.user)
    if request.method == 'POST':
        portfolio_asset.delete()
        return JsonResponse({'success': True})
    return render(request, 'investments/delete_portfolio_asset.html', {'portfolio_asset': portfolio_asset})