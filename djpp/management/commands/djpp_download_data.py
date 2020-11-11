from django.core.management import BaseCommand
from djpp.models import Product, Plan


class Command(BaseCommand):
    help = 'Syncs all data from upstream Paypal'

    def handle(self, *args, **kwargs):
        print('# Downloading products\n')
        Product.init_from_api()

        print('# Downloading plans\n')
        Plan.init_from_api()
