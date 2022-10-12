from collections import OrderedDict
from datetime import date
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from .forms import UserForm
from .models import Product, User, PriceHistory, ProductToUser
from bs4 import BeautifulSoup
import requests
import shutil
import secrets
import os
from django.views.generic.base import TemplateView 
from django.views.generic import DetailView
from django.views import View
import pygal
from django.views.generic.edit import DeleteView
from django.core.mail import send_mail




# Create your views here.

brand_specs = {'Frankie_Shop':
                {'price': ("strong", {"class": "prd-DetailPrice_Price"}),
                 'image': ("div", {"class": "prd-Detail_Image"})
                },
            'ByParra':
                 {'price': ("h2", {"class": "price"}),
                 'image' : ("div", {"class": "gallery_images"})
                 },
            'Ganni':
                 {'price_sale': ("span", {"class": "product-price__sales"}),
                 'price_regular': ("span", {"class": "product-price__normal"}),
                 'image' : ("div", {"class": "b-product-images__large"}),
                 }
            }


class IndexView(View):
    def post(self,request):
        user_form = UserForm(request.POST)
        my_url = ""

        if user_form.is_valid():
            user_data = user_form.cleaned_data
            user_url = user_data['product_url']
            soup = self.scrape_from_url(user_url)
            product_name,product_brand = self.fetch_name_brand(user_url, soup)
            out_src, new_img = self.fetch_image(product_brand, soup)
            
            user_product=Product.objects.get_or_create(
                product_url=user_url, 
                name=product_name, 
                brand=product_brand,
                img_out_src=out_src, 
                img=new_img)

            user = User.objects.get_or_create(user_email=user_data['user_email'])

            first_price = self.fetch_price(user_product[0], soup)
            product_price = PriceHistory(linked_product=user_product[0], price=first_price)
            product_price.save()

            product_to_user = ProductToUser.objects.filter(user_id=user[0], linked_product=user_product[0]).first()
            if not product_to_user:
                new_prod_user = ProductToUser(user_id=user[0], linked_product=user_product[0], desired_price=user_data["desired_price"], auth_token = self.auth_token())
                new_prod_user.save()

                #redirect to thank-you URL
                base_url = reverse('submit-sucessful')  # 1 thank-you/
                query_string =  urlencode({'auth': new_prod_user.auth_token})  # 2 auth=bhejwbhr374637hfd
                my_url = '{}?{}'.format(base_url, query_string)  # 3 /thank-you/?auth=bhejwbhr374637hfd

                send_mail(
                        'Price Monitor - you started monitoring a new product',
                        f'Hey! \nYou\'re now monitoring prices for {user_product[0].name.title()}.\nHere is your product\'s link: http://127.0.0.1:8000/auth={new_prod_user.auth_token}',
                        'fashionpricetracker@gmail.com',
                        [user[0].user_email],
                        fail_silently=False,)

            else:
                if user_data["desired_price"] != product_to_user.desired_price:
                    product_to_user.price_alt = "True"
                else:
                    product_to_user.price_alt = "False"
                
                product_to_user.save()

                #redirect to submit repeat URL
                base_url = reverse('duplicate')  # 1 duplicate/
                query_string =  urlencode({'auth': product_to_user.auth_token, 'new-price': user_data["desired_price"]}) # 2 auth=bhejwbhr374637hfd
                my_url = '{}?{}'.format(base_url, query_string)  # 3 /duplicate/?auth=bhejwbhr374637hfd&new-pre=120

            return redirect(my_url)

    def get(self,request):
        user_form = UserForm(request.GET)
        return render(request, "checker/index.html", {'form' : user_form})

    #create a detail view for product page

    def scrape_from_url(self, product_url):
    
        headers = {'user-agent': 
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}

        r = requests.get(url=product_url, headers=headers)

        # parse content through beautifulsoup parser.
        soup = BeautifulSoup(r.content, "html.parser")

        return soup

    def fetch_name_brand(self,product_url, soup):

        if "ganni" in product_url:
            brand = "Ganni"

        elif "thefrankieshop" in product_url:
            brand = "Frankie_Shop"

        elif "byparra" in product_url:
            brand = "ByParra"

        # get product's name
        name = soup.find_all("h1")[0].text

        return (name, brand)

    def fetch_image(self,brand,soup):

        # get image class from dict
        image_arg_one = (brand_specs[brand]['image'])[0]
        image_arg_two = (brand_specs[brand]['image'][1]['class'])

        # find elements with the correct class name
        div_tag = soup.select(f"{image_arg_one}.{image_arg_two}")

        images = div_tag[0].find('img')

        img_src = images['src']

        img_src_link = "http://"

        if img_src.startswith("https://") or img_src.startswith("http://"):
            img_src_link = img_src
            
        elif img_src.startswith("//"):
            after_http = img_src.lstrip("//")
            img_src_link += after_http

        else:
            img_src_link += img_src

        file_name = img_src_link.split("/")[-1].split(".")[0] + ".jpg"
        file_path = os.path.join("checker/static/checker/images/product_images/", file_name)

        # Open the url image, set stream to True, this will return the stream content.
        r = requests.get(img_src_link, stream=True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            # Open a local file with wb ( write binary ) permission.
            with open(file_path, 'wb') as file:
                shutil.copyfileobj(r.raw, file)

        file_path= "checker/images/product_images/" + file_name

        return (img_src, file_path)

    def fetch_price(self,product, soup):

        brand = product.brand

        if brand == 'Ganni':
            arg = ['price_sale', 'price_regular']
        else:
            arg = ['price']

        for tag in arg:
            price_arg_one = (brand_specs[brand][tag])[0]
            price_arg_two = (brand_specs[brand][tag][1]['class'])

            # find specific tag in parsed content and get the text element out of it.
            price = soup.find_all(price_arg_one, price_arg_two)[0].text
            if price == "": 
                continue

            int_price = int(''.join(v for v in price if v.isdigit()))
            if brand == "ByParra":
                corrected_price = str(int_price)[:-2]
                int_price = corrected_price

            return int_price

    def auth_token(self):
        user_token = secrets.token_urlsafe(16)
        return user_token

class ThanksView(View):
    def get(self, request):
        product_auth = request.GET.get('auth')
        return render(request, "checker/submit_sucess.html", {'product_auth' : product_auth})


class RepeatedSubmission(View):
    def get_object(self):
        return ProductToUser.objects.get(pk=self.request.GET.get('auth'))

    def get_title(self):
        return self.get_object().linked_product.name.title()

    def get(self,request):
        return render(request, "checker/submit_duplicate.html", {'product' : self.get_object(), 'title' : self.get_title()})

    def post(self,request):
        object = self.get_object()
        object.desired_price = self.request.GET.get('new-price')
        object.save()
        return render(request, "checker/submit_change_sucessful.html", {'product' : object})
   
class ProductDetailView(DetailView):
    template_name = "checker/product_page.html"
    model = ProductToUser

    def get_context_data(self, **kwargs):
     context = super().get_context_data(**kwargs)
     product_id = self.object.linked_product.id
     price_history = PriceHistory.objects.filter(linked_product__id=product_id)
     context["product_auth"] = self.object.auth_token
     context["product"] = self.object.linked_product
     context["title"] = self.object.linked_product.name.title()
     context["current_price"], context["graph"] = self.last_price_and_graph(price_history)
     return context

    def last_price_and_graph(self, price_history):
        price_to_date = OrderedDict()
        for entry in price_history:
            entry_date = entry.date.strftime('%d-%m-%Y')
            entry_price = entry.price
            price_to_date[entry_date] = entry_price
            product_id = entry.linked_product.id

   
        # create a line chart with pygal's pre-built LightColorizedStyle style and 20degree x label rotation.
        line_chart = pygal.Line(x_label_rotation=20)

        # chart title
        today = date.today()
        today_formatted = today.strftime("%d/%m/%Y")
        line_chart.title = today_formatted

        date_list = []
        price_list = []
    
        # loop through price_to_dat key,value pairs.
        for key, value in price_to_date.items():
            if key not in date_list:
                date_list.append(key)
                price_list.append(value)

        line_chart.x_labels = date_list   
        line_chart.add("Price", price_list)
        chart_name = str(product_id) + ".svg"
        chart_path = os.path.join("checker/static/checker/images/price_charts/", chart_name)

        line_chart.render_to_file(chart_path)

        chart_path= "checker/images/price_charts/" + chart_name

        last_date, last_price = self.last(price_to_date)

        return last_price, chart_path
    
    def last(self, ord_dict):
        last_item = next(reversed(ord_dict.items()))
        return last_item

class DeleteProductView(DeleteView):
    model = ProductToUser
    template_name = "checker/delete_confirm.html"
    success_url = reverse_lazy("delete-sucessful")

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['title'] = self.object.linked_product.name.title()
        return context

class DeleteSucessful(TemplateView):
    template_name = "checker/delete_sucess.html"

class ContactView(View):
    def get(self,request):
        return render(request, "checker/contact.html")

    def post(self, request):
        user_data = request.POST
        user_name = user_data['name']
        user_email = user_data['email']
        message_subject= user_data['subject']
        message_content = user_data['message']
        send_mail(
            'New user message',
            f'Name:{user_name}\nEmail:{user_email}\nSubject:{message_subject}\nMessage:{message_content}', 
            'fashionpricetracker@gmail.com',
            ['fashionpricetracker@gmail.com'],
            fail_silently=False,)
        return redirect('contact-us/sucess')

class ContactSucessView(TemplateView):
    template_name = "checker/contact_sucess.html"