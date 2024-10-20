import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Portfolio, Asset, PortfolioAsset, TotalValueHistory
from . import utils
from . import api
from django.utils import timezone
from unittest.mock import patch
import json


# Create your tests here.
User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')


@pytest.fixture
def portfolio(user):
    return Portfolio.objects.create(user=user, name='Test Portfolio', currency='USD')


@pytest.fixture
def asset():
    return Asset.objects.create(name='Test Asset', symbol='TEST', asset_type='Stock', latest_price=100, currency='USD')


@pytest.fixture
def portfolio_asset(portfolio, asset):
    return PortfolioAsset.objects.create(portfolio=portfolio, asset=asset, position=10)


# Model Tests
@pytest.mark.django_db
class TestModels:
    def test_portfolio_creation(self, user):
        portfolio = Portfolio.objects.create(user=user, name='New Portfolio', currency='USD')
        assert portfolio.name == 'New Portfolio'
        assert portfolio.currency == 'USD'

    def test_asset_creation(self):
        asset = Asset.objects.create(name='New Asset', symbol='NEW', asset_type='Stock', latest_price=50, currency='USD')
        assert asset.name == 'New Asset'
        assert asset.latest_price == 50

    def test_portfolio_asset_creation(self, portfolio, asset):
        portfolio_asset = PortfolioAsset.objects.create(portfolio=portfolio, asset=asset, position=5)
        assert portfolio_asset.position == 5

    def test_total_value_history_creation(self, user):
        history = TotalValueHistory.objects.create(user=user, total_value=1000)
        assert history.total_value == 1000
        assert history.timestamp is not None


# View Tests
@pytest.mark.django_db
class TestViews:
    def test_dashboard_view(self, client, user):
        client.force_login(user)
        response = client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert 'total_value' in response.context

    def test_list_portfolios_view(self, client, user, portfolio):
        client.force_login(user)
        response = client.get(reverse('list_portfolios'))
        assert response.status_code == 200
        assert len(response.context['portfolios']) == 1

    def test_add_portfolio_view(self, client, user):
        client.force_login(user)
        response = client.post(reverse('add_portfolio'), {'name': 'New Portfolio', 'currency': 'USD'})
        assert response.status_code == 302
        assert Portfolio.objects.filter(name='New Portfolio').exists()

    def test_portfolio_detail_view(self, client, user, portfolio, portfolio_asset):
        client.force_login(user)
        response = client.get(reverse('portfolio_detail', kwargs={'portfolio_id': portfolio.id}))
        assert response.status_code == 200
        assert response.context['portfolio'] == portfolio

    @patch('investments.api.search_assets')
    def test_search_assets_view(self, mock_search, client, user):
        mock_search.return_value = [{'symbol': 'AAPL', 'name': 'Apple Inc.'}]
        client.force_login(user)
        response = client.get(reverse('search_assets'), {'q': 'Apple'})
        assert response.status_code == 200
        assert 'AAPL' in response.json()['results'][0]['symbol']

    def test_add_assets_view(self, client, user, portfolio):
        client.force_login(user)
        data = {'assets': [{'symbol': 'AAPL', 'quantity': 10}]}
        response = client.post(reverse('add_assets', kwargs={'portfolio_id': portfolio.id}), 
                               data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        assert PortfolioAsset.objects.filter(portfolio=portfolio, asset__symbol='AAPL').exists()


# Utility Tests
@pytest.mark.django_db
class TestUtils:
    def test_convert_currency(self):
        with patch('investments.api.get_exchange_rate', return_value=0.85):
            result = utils.convert_currency(Decimal('100'), 'USD', 'EUR')
            assert result == Decimal('85')

    def test_get_portfolio_value(self, portfolio, portfolio_asset):
        value = utils.get_portfolio_value(portfolio)
        assert value == Decimal('1000')  # 10 shares * $100 per share

    @patch('investments.utils.api.get_asset_data')
    def test_create_asset(self, mock_get_asset_data):
        mock_get_asset_data.return_value = {
            'AAPL': {
                'name': 'Apple Inc.',
                'asset_type': 'Stock',
                'latest_price': 150,
                'currency': 'USD'
            }
        }
        asset = utils.create_asset('AAPL')
        assert asset.name == 'Apple Inc.'
        assert asset.latest_price == 150


# API Tests
@pytest.mark.django_db
class TestAPIIntegration:
    @patch('investments.api.yf.Tickers')
    def test_get_asset_data(self, mock_tickers):
        mock_ticker = mock_tickers.return_value.tickers['AAPL']
        mock_ticker.info = {
            'shortName': 'Apple Inc.',
            'longName': 'Apple Inc.',
            'quoteType': 'EQUITY',
            'previousClose': 235.0,
            'currentPrice': 235.0, 
            'currency': 'USD'
        }
        data = api.get_asset_data(['AAPL'])
        assert 'AAPL' in data
        assert data['AAPL']['name'] == 'Apple Inc.'
        assert data['AAPL']['latest_price'] == 235.0
        assert data['AAPL']['asset_type'] == 'EQUITY'
        assert data['AAPL']['currency'] == 'USD'

    @patch('investments.api.requests.get')
    def test_get_exchange_rate(self, mock_get):
        mock_get.return_value.json.return_value = {
            'result': 'success',
            'conversion_rates': {'EUR': 0.85}
        }
        rate = api.get_exchange_rate('USD', 'EUR')
        assert rate == Decimal('0.85')