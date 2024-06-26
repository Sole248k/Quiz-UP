from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth import authenticate, login
from .models import *
from .forms import *

# Create your views here.
def landing(request):
    context={}
    return render(request, "quiz_up_app/landing.html", context)

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('landing')  
        else:
            return render(request, 'quiz_up_app/signin.html', {'error': 'Invalid username or password'})
        
   
    return render(request, 'quiz_up_app/signin.html')

def signup(request):
    if request.method == 'POST':
        form = signup(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if new_user:
                login(request, new_user)
                return redirect('landing')  
        else:
            pass
    else:
        form = UserForm()
    return render(request, 'quiz_up_app/signup.html', {'form': form})