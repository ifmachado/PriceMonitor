from django.forms import ModelForm
from django import forms


class UserForm(forms.Form):
    product_url = forms.URLField(max_length=200)
    user_email = forms.EmailField()
    desired_price = forms.IntegerField()

