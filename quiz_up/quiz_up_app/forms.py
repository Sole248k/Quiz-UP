from django import forms
from .models import *

from django.contrib.auth.hashers import check_password

class UserForm(forms.ModelForm):

    class Meta:
        model = Users
        fields = ['firstname', 'lastname', 'username', 'email', 'password']
