from django.contrib import admin
from .models import ProductToUser, User, Product, PriceHistory

# Register your models here.

class PriceHistoryAdmin(admin.ModelAdmin):
    fields = ("linked_product", "price")
    readonly_fields = ("date",)
    list_display = ("linked_product", "date", "price")
    list_filter = ("linked_product", "date")

    class Meta:
        verbose_name ="PriceHistory"
        verbose_name_plural = "PriceHistory"

 

admin.site.register(User) 
admin.site.register(Product) 
admin.site.register(PriceHistory,PriceHistoryAdmin) 
admin.site.register(ProductToUser) 
