from django.contrib import admin
from .models import ProductToUser, User, Product, PriceHistory

# Setting up configs for readonly fields and displayed and filtered fields on admin panel.


class PriceHistoryAdmin(admin.ModelAdmin):
    fields = ("linked_product", "price")
    readonly_fields = ("price_date",)
    list_display = ("linked_product", "price_date", "price")
    list_filter = ("linked_product", "price_date")


class ProductToUserAdmin(admin.ModelAdmin):
    fields = ("user_id", "linked_product", "desired_price",
              "auth_token", "price_alt", "price_email_sent")
    list_display = ("user_id", "linked_product")
    list_filter = ("user_id", "linked_product", "auth_token")


# register models and admin config classes to admin panel
admin.site.register(User)
admin.site.register(Product)
admin.site.register(PriceHistory, PriceHistoryAdmin)
admin.site.register(ProductToUser, ProductToUserAdmin)
