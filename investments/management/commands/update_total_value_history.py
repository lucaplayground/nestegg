from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from investments.models import TotalValueHistory
from investments.utils import get_total_value

User = get_user_model()


class Command(BaseCommand):
    help = 'Update total value history for all users'

    def handle(self, *args, **options):
        today = timezone.now().date()
        for user in User.objects.all():
            total_value = get_total_value(user)

            TotalValueHistory.objects.update_or_create(
                user=user,
                timestamp__date=today,
                defaults={'total_value': total_value, 'timestamp': timezone.now()}
            )

        self.stdout.write(self.style.SUCCESS('Successfully updated total value history for all users'))