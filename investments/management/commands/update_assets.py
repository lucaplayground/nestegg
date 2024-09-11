from django.core.management.base import BaseCommand
from investments.utils import update_asset_data
from investments.models import Asset


class Command(BaseCommand):
    help = "Update prices from Yahoo Finance for all existing assets"

    def handle(self, *args, **options):
        # Fetch all asset symbols from the database
        assets = Asset.objects.all()

        if not assets:
            self.stdout.write(self.style.WARNING('No assets found in the database.'))
            return
        
        for asset in assets:
            # Call the function to update asset data
            updated_asset = update_asset_data(asset.symbol)
            if updated_asset:
                self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_asset.name} ({updated_asset.symbol})'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to update {asset.symbol}'))