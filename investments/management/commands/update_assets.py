from django.core.management.base import BaseCommand
from investments.utils import update_all_assets
from investments.models import Asset
import time


class Command(BaseCommand):
    help = 'Updates the latest prices for all assets'

    def handle(self, *args, **options):
        updated_count, failed_count = update_all_assets()
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} assets'))
        if failed_count > 0:
            self.stdout.write(self.style.WARNING(f'Failed to update {failed_count} assets'))