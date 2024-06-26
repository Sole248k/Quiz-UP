from django import forms
from .models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['username', 'email', 'password']
        
