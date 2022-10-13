from django.core.management.base import BaseCommand, CommandError
from checker.models import PriceHistory, ProductToUser
from django.core.mail import send_mail



class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **kwargs):  
        products_to_users = ProductToUser.objects.all()
        for entry in products_to_users:
            current_product = entry.linked_product
            current_user = entry.user_id
            desired_price = entry.desired_price
            product_prices = PriceHistory.objects.filter(linked_product=current_product).order_by('price')
            lowest_price = product_prices[0].price
            if lowest_price <= desired_price and entry.price_email_sent==False:
                send_mail(
                        'Price Monitor - your product reached the target price!',
                        f'Hey! \n{current_product.name.title()} has reached your target price of {desired_price}. \nHere is your product\'s link: http://127.0.0.1:8000/auth={entry.auth_token}',
                        'fashionpricetracker@gmail.com',
                        [current_user.user_email],
                        fail_silently=False,)
                entry.price_email_sent=True
                entry.save()

                self.stdout.write(self.style.SUCCESS('Email sucessfully sent to user'))