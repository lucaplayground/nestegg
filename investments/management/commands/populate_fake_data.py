from django.core.management.base import BaseCommand
from investments.models import Portfolio, Asset, PortfolioAsset, PositionHistory
from django.contrib.auth.models import User
from investments.utils import update_asset_data
import random


class Command(BaseCommand):
    help = "Populate the database with fake data for testing"

    def handle(self, *args, **options):
        # Clear existing data
        PortfolioAsset.objects.all().delete()  # Clear PortfolioAsset first to avoid foreign key issues
        PositionHistory.objects.all().delete()  # Clear PositionHistory
        Asset.objects.all().delete()  # Clear Asset
        Portfolio.objects.all().delete()  # Clear Portfolio
        User.objects.all().delete()  # Clear existing users

        # Create a test user
        user = User.objects.create_user(username='testuser', password='P@ssword123')

        # Create some fake portfolios
        portfolios = []
        for i in range(3):  # Create 3 portfolios
            portfolio = Portfolio.objects.create(user=user, name=f'Test Portfolio {i + 1}')
            portfolios.append(portfolio)

        # Create some fake assets
        asset_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        for symbol in asset_symbols:
            # Create the asset with predefined data
            asset = Asset.objects.create(
                symbol=symbol,
                name=f'Fake Asset {symbol}',
                asset_type='Stock',
                latest_price=random.uniform(100, 1500),  # Random price between 100 and 1500
                currency='USD'
            )

            # Update the asset data using the API
            updated_asset = update_asset_data(symbol)
            if updated_asset:
                self.stdout.write(self.style.SUCCESS(f'Successfully updated asset data for {updated_asset.name} ({updated_asset.symbol})'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to update asset data for {symbol}'))

            # Assign assets to portfolios with random positions
            for portfolio in portfolios:
                position = random.randint(1, 100)  # Random position between 1 and 100
                portfolio_asset = PortfolioAsset.objects.create(
                    portfolio=portfolio,
                    asset=asset,
                    position=position
                )
                # Create a PositionHistory entry
                portfolio_asset.position_history.create(
                    position=position,
                    price_at_time=asset.latest_price
                )
        self.stdout.write(self.style.SUCCESS('Successfully populated the database with fake data and updated asset prices.'))
