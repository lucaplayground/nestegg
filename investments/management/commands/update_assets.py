from django.core.management.base import BaseCommand
from investments.utils import update_asset_price
from investments.models import Asset
import time


class Command(BaseCommand):
    help = "Update latest prices from Yfinance for all existing assets"

    def handle(self, *args, **options):
        # Fetch all asset symbols from the database
        assets = Asset.objects.all()

        if not assets:
            self.stdout.write(self.style.WARNING('No assets found in the database.'))
            return
        
        for asset in assets:
            # Call utility function to update the price for each asset
            updated_asset = update_asset_price(asset)
            if updated_asset:
                self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_asset.name} ({updated_asset.symbol})'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to update {asset.symbol}'))

        # Add a delay to avoid overwhelming the API
        time.sleep(1)