from collections import OrderedDict
from datetime import date
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from .forms import ContactForm, UserForm
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
from .static.checker.graph_style import custom_style as graph_syle



# Create your views here.

#Dict stores HTML and CSS info extracted from product URLs so the correct tags can be found when scraping.
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
                base_url = reverse('submit-successful')  # 1 thank-you/
                query_string =  urlencode({'auth': new_prod_user.auth_token})  # 2 auth=bhejwbhr374637hfd
                my_url = '{}?{}'.format(base_url, query_string)  # 3 /thank-you/?auth=bhejwbhr374637hfd

                # sends email to user confirming submition success.
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

    # when page receives a GET request, it renders the class based user/product form and the index hmtl, passing the form as context.
    def get(self,request):
        user_form = UserForm(request.GET)
        return render(request, "checker/index.html", {'form' : user_form})

    def scrape_from_url(self, product_url):  
        # headers included to prevent page from block the script when scraping.
        headers = {'user-agent': 
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}

        # get HTML document from URL usign requests lib and passing headers as arg
        r = requests.get(url=product_url, headers=headers)

        # parse content through beautifulsoup parser.
        soup = BeautifulSoup(r.content, "html.parser")

        return soup

    def fetch_name_brand(self,product_url, soup):
        # check which brand name is in URL to define brand name:
        if "ganni" in product_url:
            brand = "Ganni"

        elif "thefrankieshop" in product_url:
            brand = "Frankie_Shop"

        elif "byparra" in product_url:
            brand = "ByParra"

        # get product's name by finding the first H1 HTML tag in soup objects.
        name = soup.find_all("h1")[0].text

        return (name, brand)

    def fetch_image(self,brand,soup):

        # get image class from dict
        image_arg_one = (brand_specs[brand]['image'])[0]
        image_arg_two = (brand_specs[brand]['image'][1]['class'])

        # find elements with the correct class name
        div_tag = soup.select(f"{image_arg_one}.{image_arg_two}")

        #from the list of divs, get only the img tags.
        images = div_tag[0].find('img')

        #from the img tag, get only the src attribute.
        img_src = images['src']

        #configure source path in proper http:// or https:// format.
        img_src_link = "http://"

        if img_src.startswith("https://") or img_src.startswith("http://"):
            img_src_link = img_src
            
        elif img_src.startswith("//"):
            after_http = img_src.lstrip("//")
            img_src_link += after_http

        else:
            img_src_link += img_src

        #configure name of image file to be saved
        file_name = img_src_link.split("/")[-1].split(".")[0] + ".jpg"

        #configure path of image file to be saved
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

        #full path
        file_path= "checker/images/product_images/" + file_name

        return (img_src, file_path)

    def fetch_price(self,product, soup):

        #get brand attribure from product object
        brand = product.brand

        #Ganni has two types of tags classes that hold the product's price depending if it's on sale.
        if brand == 'Ganni':
            arg = ['price_sale', 'price_regular']
        else:
            arg = ['price']

        #loop through args and get corresponding tag class from dict
        for tag in arg:
            price_arg_one = (brand_specs[brand][tag])[0]
            price_arg_two = (brand_specs[brand][tag][1]['class'])

            # find specific tag in parsed content and get the text element out of it.
            price = soup.find_all(price_arg_one, price_arg_two)[0].text
            if price == "": 
                continue

            #casting price value as and int and removing any extra characters
            int_price = int(''.join(v for v in price if v.isdigit()))

            #ByParra prices are returned with 2 zeros after decimal point and should be removed.
            if brand == "ByParra":
                corrected_price = str(int_price)[:-2]
                int_price = corrected_price

            return int_price

    # generate token for user to product relation identification
    def auth_token(self):
        user_token = secrets.token_urlsafe(16)
        return user_token

# Renders submit_success HTML, gets auth token passed through URL and passed that as context to HTML.
class ThanksView(View):
    def get(self, request):
        product_auth = request.GET.get('auth')
        return render(request, "checker/submit_success.html", {'product_auth' : product_auth})


class RepeatedSubmission(View):
    # get ProducttoUser object that matches the pk passed through URL
    def get_object(self):
        return ProductToUser.objects.get(pk=self.request.GET.get('auth'))

    #get product title from Product object attribute
    def get_title(self):
        return self.get_object().linked_product.name.title()

    # when page receives a GET request, it renders the submit_duplicate hmtl, passing the the ProductToUser object and the product title as context.
    def get(self,request):
        return render(request, "checker/submit_duplicate.html", {'product' : self.get_object(), 'title' : self.get_title()})

    # when POST request is received from form (meaning user submitted a new price),
    # it replaces the object's desired_price attribute value with the new price submitted.
    # also renderes the submit_change_successful.html with the ProducttoUSer object as context.
    def post(self,request):
        object = self.get_object()
        object.desired_price = self.request.GET.get('new-price')
        object.save()
        return render(request, "checker/submit_change_successful.html", {'product' : object})

#View for product page, it extends Django's generic DetailView as it's ideal to displaying info related to a single object from a Model.
class ProductDetailView(DetailView):
    template_name = "checker/product_page.html"
    model = ProductToUser

    #adding auth_token, product object, title, price and graph to context to be passed to HTML
    def get_context_data(self, **kwargs):
     context = super().get_context_data(**kwargs)
     product_id = self.object.linked_product.id
     price_history = PriceHistory.objects.filter(linked_product__id=product_id)
     context["product_auth"] = self.object.auth_token
     context["product"] = self.object.linked_product
     context["title"] = self.object.linked_product.name.title()
     context["current_price"], context["graph"] = self.last_price_and_graph(price_history)
     return context

    #gets last price in DB for specific product and generates a price history graph
    def last_price_and_graph(self, price_history):
        price_to_date = OrderedDict()
        
        #loop through all the PriceHistory objects in the price_history list.
        for entry in price_history:

            # get object's date attribute and format it
            entry_date = entry.date.strftime('%d-%m-%Y')

            # get object's price attribute
            entry_price = entry.price

            #add date and price to OrderedDict
            price_to_date[entry_date] = entry_price

            product_id = entry.linked_product.id

        #create a line chart with pygal using custom style.
        line_chart = pygal.Line(x_label_rotation=20, style=graph_syle)

        # chart title
        today = date.today()
        today_formatted = today.strftime("%d/%m/%Y")
        line_chart.title = today_formatted

        date_list = []
        price_list = []
    
        # loop through price_to_date key,value pairs to add each date to date_list and price to price_list
        for key, value in price_to_date.items():
            if key not in date_list:
                date_list.append(key)
                price_list.append(value)

        #x labels for chart are dates
        line_chart.x_labels = date_list   

        #y values are the prices
        line_chart.add("Price", price_list)

        #config name for chart to be saved as an svg file
        chart_name = str(product_id) + ".svg"

         #config paath for chart to be saved
        chart_path = os.path.join("checker/static/checker/images/price_charts/", chart_name)

        #render line chart to path defined above
        line_chart.render_to_file(chart_path)

        chart_path= "checker/images/price_charts/" + chart_name

        #get most recent price from OrderedDict with all prices.
        last_date, last_price = self.last(price_to_date)

        return last_price, chart_path
    
    # gets ordered dict and returns its last item.
    def last(self, ord_dict):
        last_item = next(reversed(ord_dict.items()))
        return last_item

# Renders delete-confirm html, deletes the specific instance of Product to User model (object is identified through pk passed through URL to this view)
# and redirects to success url
# Product title is passed as context to delete-confirm html.
class DeleteProductView(DeleteView):
    model = ProductToUser
    template_name = "checker/delete_confirm.html"
    success_url = reverse_lazy("delete-successful")

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['title'] = self.object.linked_product.name.title()
        return context

# Delete success page only requires a html to be rendered.
class DeleteSuccessful(TemplateView):
    template_name = "checker/delete_success.html"

class ContactView(View):
    # when page receives a GET request, it renders the class based contact form and the contact hmtl, passing the form as context.
    def get(self,request):
        contact_form = ContactForm(request.GET)
        return render(request, "checker/contact.html", {'form' : contact_form})

    # when POST request is received from form, it stores its info under specific vars 
    # and sends email to admin email with user message details.
    def post(self, request):
        user_data = request.POST
        user_name = user_data['user_name']
        user_email = user_data['user_email']
        message_subject= user_data['subject']
        message_content = user_data['message']
        send_mail(
            'New user message',
            f'Name:{user_name}\nEmail:{user_email}\nSubject:{message_subject}\nMessage:{message_content}', 
            'fashionpricetracker@gmail.com',
            ['fashionpricetracker@gmail.com'],
            fail_silently=False,)
        return redirect('contact-us/success')

# Contact success page only requires a html to be rendered.
class ContactSuccessView(TemplateView):
    template_name = "checker/contact_success.html"