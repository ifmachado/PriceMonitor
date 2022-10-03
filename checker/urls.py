from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='starting-page'),
    path('thank-you', views.ThanksView.as_view(), name='submit-sucessful'),
    path('auth=<str:pk>', views.ProductDetailView.as_view(), name="product-page"),

]