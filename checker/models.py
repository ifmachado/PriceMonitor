from django.db import models

# Create your models here.

class Product(models.Model):
    product_url = models.URLField(max_length=200)
    brand = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    img_out_src = models.URLField(max_length=200)
    img = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.brand} - {self.name}"


class User(models.Model):
    user_email = models.EmailField(primary_key=True)

    def __str__(self):
        return self.user_email

class ProductToUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    linked_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    desired_price = models.IntegerField()
    auth_token = models.CharField(max_length=20, primary_key=True)
    price_alt = models.CharField(max_length=5, default="False")


    def __str__(self):
        return f"{self.user_id.user_email} - {self.linked_product.name}"

class PriceHistory(models.Model):
    linked_product = models.ForeignKey(Product, related_name="current_product", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    price = models.IntegerField(null=True)

    def __str__(self):
        return self.linked_product.name



