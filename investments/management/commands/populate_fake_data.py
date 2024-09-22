from django.core.management.base import BaseCommand
from investments.models import Portfolio, Asset, PortfolioAsset, PositionHistory
from django.contrib.auth import get_user_model
from investments.utils import create_asset, create_position_history
import random
import time


class Command(BaseCommand):
    help = "Clear existing data and populate the database with fake data for testing"

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing data...')
        # Clear existing data
        PortfolioAsset.objects.all().delete()  # Clear PortfolioAsset first to avoid foreign key issues
        PositionHistory.objects.all().delete()  # Clear PositionHistory
        Asset.objects.all().delete()  # Clear Asset
        Portfolio.objects.all().delete()  # Clear Portfolio
        
        # Clear existing users if exists
        User = get_user_model()  # get the custom user model
        User.objects.all().delete()

        self.stdout.write('Creating new fake data...')
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
            updated_asset = create_asset(symbol)
            if updated_asset:
                self.stdout.write(self.style.SUCCESS(f'Successfully updated asset data for {updated_asset.name} ({updated_asset.symbol})'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to update asset data for {symbol}'))

            time.sleep(2)  # Add a delay of 2 seconds between requests    

            # Assign assets to portfolios with random positions
            for portfolio in portfolios:
                position = random.randint(1, 100)  # Random position between 1 and 100
                portfolio_asset = PortfolioAsset.objects.create(
                    portfolio=portfolio,
                    asset=asset,
                    position=position
                )
                # Create a PositionHistory entry
                create_position_history(portfolio_asset, position)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with fake data and updated asset prices.'))
