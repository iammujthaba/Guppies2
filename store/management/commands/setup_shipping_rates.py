from django.core.management.base import BaseCommand
from store.models import ShippingRate

class Command(BaseCommand):
    help = 'Set up initial shipping rates'

    def handle(self, *args, **kwargs):
        rates = [
            ('Kerala', 100, 20),
            ('Karnataka', 120, 30),
            ('Tamil Nadu', 120, 30),
        ]

        for state, base_rate, additional_rate in rates:
            ShippingRate.objects.get_or_create(
                state=state,
                defaults={'base_rate': base_rate, 'additional_item_rate': additional_rate}
            )

        self.stdout.write(self.style.SUCCESS('Successfully set up shipping rates'))