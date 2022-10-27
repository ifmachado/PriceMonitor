from django.urls import path
from . import views

#sets up URLConfig for each URL path, including which function should be called when page there's a browser request to that URL
urlpatterns = [
    path('', views.IndexView.as_view(), name='starting-page'),
    path('thank-you/', views.ThanksView.as_view(), name='submit-successful'),
    path('duplicate/', views.RepeatedSubmission.as_view(), name='duplicate'),
    path('change-successful/', views.RepeatedSubmission.as_view(), name='change-successful'),

    #dinamically constructed urls, where data passed through URL will be a string and a primary key for ProductToUser model.
    path('auth=<str:pk>', views.ProductDetailView.as_view(), name="product-page"), 
    path('delete=<str:pk>', views.DeleteProductView.as_view(), name="confirm-delete"),
    
    path('delete-successful', views.DeleteSuccessful.as_view(), name="delete-successful"),
    path('contact-us', views.ContactView.as_view(), name="contact-us"),
    path('contact-us/success', views.ContactSuccessView.as_view(), name="contact-success"),

]