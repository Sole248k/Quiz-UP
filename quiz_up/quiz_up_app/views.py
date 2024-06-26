from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def landing(request):
    context={}
    return render(request, "quiz_up_app/landing.html", context)