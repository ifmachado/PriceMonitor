from django.urls import path
from . import views

#sets up URLConfig for each URL path, including which function should be called when page there's a browser request to that URL
urlpatterns = [
    path('', views.IndexView.as_view(), name='starting-page'),
    path('thank-you/', views.ThanksView.as_view(), name='submit-sucessful'),
    path('duplicate/', views.RepeatedSubmission.as_view(), name='duplicate'),
    path('change-sucessful/', views.RepeatedSubmission.as_view(), name='change-sucessful'),

    #dinamically constructed urls, where data passed through URL will be a string and a primary key for ProductToUser model.
    path('auth=<str:pk>', views.ProductDetailView.as_view(), name="product-page"), 
    path('delete=<str:pk>', views.DeleteProductView.as_view(), name="confirm-delete"),

    path('delete-sucessful', views.DeleteSucessful.as_view(), name="delete-sucessful"),
    path('contact-us', views.ContactView.as_view(), name="contact-us"),
    path('contact-us/sucess', views.ContactSucessView.as_view(), name="contact-sucess"),

]