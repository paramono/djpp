from django.core.management import BaseCommand
from djpaypal_subs.models import Product, Plan


class Command(BaseCommand):
    help = 'Syncs all data from upstream Paypal'

    def handle(self, *args, **kwargs):
        print('Downloading products')
        Product.init_from_api()

        print('Downloading plans')
        Plan.init_from_api()
