from django.core.management.base import BaseCommand
from investments.models import Portfolio, Asset, PortfolioAsset, TotalValueHistory
from django.contrib.auth import get_user_model
from investments.utils import create_asset, get_total_value, update_total_value_history
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = "Clear existing data and populate the database with fake data for testing"

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing data...')
        # Clear existing data
        PortfolioAsset.objects.all().delete()  # Clear PortfolioAsset first to avoid foreign key issues
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
        asset_symbols = ['AAPL', '161005.SZ', 'VT', 'FNZ.NZ', 'BIL']
        for symbol in asset_symbols:
            asset = create_asset(symbol)
            if asset:
                self.stdout.write(self.style.SUCCESS(f'Successfully created/updated asset: {asset.name} ({asset.symbol})'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to create/update asset for {symbol}'))

            if asset:
                # Assign assets to portfolios with random positions
                for portfolio in portfolios:
                    position = random.randint(1, 100)  # Random position between 1 and 100
                    portfolio_asset = PortfolioAsset.objects.create(
                        portfolio=portfolio,
                        asset=asset,
                        position=position
                    )
            
            time.sleep(2)  # Add a delay of 2 seconds between requests 

        # Add total value history for the test user
        self.stdout.write('Creating total value history...')
        start_date = datetime.now() - timedelta(days=30)  # Start from 30 days ago
        for i in range(31):  # Create 31 data points (one for each day)
            date = start_date + timedelta(days=i)
            total_value = get_total_value(user)
            # Convert to float, apply randomness, then convert back to Decimal
            total_value = Decimal(str(float(total_value) * random.uniform(0.95, 1.05)))
            TotalValueHistory.objects.create(
                user=user,
                timestamp=date,
                total_value=total_value
            )
            self.stdout.write(f'Created total value history for {date.date()}: {total_value}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully populated the database with fake data and updated asset prices.'))