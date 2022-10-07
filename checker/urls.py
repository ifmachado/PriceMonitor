from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='starting-page'),
    path('thank-you/', views.ThanksView.as_view(), name='submit-sucessful'),
    path('duplicate/', views.RepeatedSubmission.as_view(), name='duplicate'),
    path('change-sucessful/', views.RepeatedSubmission.as_view(), name='change-sucessful'),
    path('auth=<str:pk>', views.ProductDetailView.as_view(), name="product-page"),
    path('delete=<str:pk>', views.DeleteProductView.as_view(), name="confirm-delete"),
    path('delete-sucessful', views.DeleteSucessful.as_view(), name="delete-sucessful"),



]