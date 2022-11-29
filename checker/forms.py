from unittest.util import _MAX_LENGTH
from django import forms

# class based form for starting page. This info is used by Product, User and Product to User models.
# No labels will be displayed, therefore placeholder text is set up.


class UserForm(forms.Form):
    product_url = forms.URLField(max_length=200, widget=forms.URLInput
                                 (attrs={'placeholder': 'Product\'s URL'}))
    user_email = forms.EmailField(max_length=200, widget=forms.EmailInput
                                  (attrs={'placeholder': 'Your Email'}))
    desired_price = forms.IntegerField(widget=forms.NumberInput
                                       (attrs={'placeholder': 'Desired Price'}))

# class based form for contact us page.


class ContactForm(forms.Form):
    user_name = forms.CharField(max_length=40, label='Your name')
    user_email = forms.EmailField(max_length=200, label='Your Email')
    subject = forms.CharField(max_length=500)
    message = forms.CharField(min_length=10)

# class based form for product page - sed to update targer price


class ProductUpdateForm(forms.Form):
    new_price = forms.IntegerField(widget=forms.NumberInput(
        attrs={'placeholder': 'Desired Price'}))
