from django.core.management.base import BaseCommand, CommandError
from checker.models import PriceHistory, ProductToUser
from django.core.mail import send_mail



class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **kwargs):  
        # Returns a queryset with all objects in model. The values func will make sure that queryset is in dict form and not model instances.
        # Each of those dictionaries represents an object, with the keys corresponding to the attribute names of model objects
        products_to_users = ProductToUser.objects.all().values()
        for entry in products_to_users:
            current_product = entry['linked_product']
            current_user = entry['user_id']
            desired_price = entry['desired_price']
            auth_token = entry['auth_token']
            product_prices = PriceHistory.objects.filter(linked_product=current_product).order_by('price')
            lowest_price = product_prices[0]
            if lowest_price <= desired_price:
                send_mail(
                        'Price Monitor - your product reached the target price!',
                        f'Hey! {current_product.name.title()} has reached your target price of {desired_price}. \nHere is your product\'s link: http://127.0.0.1:8000/auth={auth_token}',
                        'fashionpricetracker@gmail.com',
                        [current_user.user_email],
                        fail_silently=False,)

                self.stdout.write(self.style.SUCCESS('Email sucessfully sent to user'))