from django.core.management.base import BaseCommand, CommandError
from checker.models import PriceHistory
from checker.views import IndexView

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **kwargs):  
        # Returns a queryset with all objects in model. The values func will make sure that queryset is in dict form and not model instances.
        # Each of those dictionaries represents an object, with the keys corresponding to the attribute names of model objects
        all_prices = PriceHistory.objects.all().values()
        for entry in all_prices:
            product = entry['linked_product']
            soup = IndexView.scrape_from_url(product.product_url)
            current_price = IndexView.fetch_price(product, soup)
            product_price = PriceHistory(linked_product=product, price=current_price)
            product_price.save()

            self.stdout.write(self.style.SUCCESS('Prices successfuly updated in model'))