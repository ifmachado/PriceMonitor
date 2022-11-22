from django.db import models

# Create your models here.

#This model is used to store product information on DB.
class Product(models.Model):
    product_url = models.URLField(max_length=20, unique=True)
    brand = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    img_out_src = models.URLField(max_length=200)
    img = models.CharField(max_length=200)

    #defines how objects from this model will be displayed when printed
    def __str__(self):
        return f"{self.brand} - {self.name}"


#This model is used to store user information on DB.
class User(models.Model):
    user_email = models.EmailField(primary_key=True)

    def __str__(self):
        return self.user_email

# This model is used to link users to the products they want to monitor. 
# It will include info like desired_price, price alteration and email_sent that only relates from a single user to a single product.
# Auth token is unique and will be user to create product URLs and identify user to product relation.
class ProductToUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    linked_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    desired_price = models.IntegerField()
    auth_token = models.CharField(max_length=30, primary_key=True)
    price_alt = models.CharField(max_length=5, default="False")
    price_email_sent=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_id.user_email} - {self.linked_product.name}"

#This model will be used to store price info scraped from product URL. 
#There will be multiple entries per product.
class PriceHistory(models.Model):
    linked_product = models.ForeignKey(Product, related_name="current_product", on_delete=models.CASCADE)
    price_date = models.DateField(auto_now=True)
    price = models.IntegerField(null=True)

    def __str__(self):
        return self.linked_product.name
    
    #defines how this model's name should be displayed when pluralized (which always happends on admin panel)
    class Meta:
        verbose_name_plural = "Price History"



