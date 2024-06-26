from django import forms
from .models import *

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, max_length=16)
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=16)

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'confirmpassword']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirmpassword = self.cleaned_data.get('confirmpassword')
        if password and confirmpassword and password != confirmpassword:
            raise forms.ValidationError("Passwords do not match")
        return confirmpassword
