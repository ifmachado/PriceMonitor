import datetime
from unittest.util import _MAX_LENGTH
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class UserForm(forms.Form):
    product_url = forms.URLField(max_length=200, widget= forms.URLInput
                           (attrs={'placeholder':'Product\'s URL'}))
    user_email = forms.EmailField(max_length=200, widget= forms.EmailInput
                           (attrs={'placeholder':'Your Email'}))
    desired_price = forms.IntegerField(widget= forms.NumberInput
                           (attrs={'placeholder':'Desired Price'}))

class ContactForm(forms.Form):
    user_name=forms.CharField(max_length=40, label='Your name')
    user_email = forms.EmailField(max_length=200, label='Your Email')
    subject = forms.CharField(max_length=500)
    message = forms.TextInput()
