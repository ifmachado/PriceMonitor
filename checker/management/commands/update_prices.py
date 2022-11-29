from django.core.management.base import BaseCommand, CommandError
from checker.models import PriceHistory, Product
from checker.views import IndexView

# creates a command that can be run from django project and crontab


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    # this function will scrape price from product url and store current value as a new entry in db

    def handle(self, *args, **kwargs):
        all_products = Product.objects.all()
        for entry in all_products:
            soup = IndexView.scrape_from_url(self, entry.product_url)
            current_price = IndexView.fetch_price(self, entry, soup)
            product_price = PriceHistory(
                linked_product=entry, price=current_price)
            product_price.save()

            self.stdout.write(self.style.SUCCESS(
                'Prices successfuly updated in model'))
