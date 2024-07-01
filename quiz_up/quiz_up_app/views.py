from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404

from .models import *
from .forms import *
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from functools import wraps
from django.db.models import Count

# Create your views here.
def landing(request):
    context={}
    return render(request, "quiz_up_app/landing.html", context)

def signin(request):
    if request.method == "GET":
        identifier = request.GET.get('identifier')
        passw = request.GET.get('password')
        now = datetime.now()
        hour = now.hour
        greeting = 'Good Morning' if 5 <= hour < 12 else ('Good afternoon' if 12 <= hour < 18 else 'Good Evening')
        try:
            user = Users.objects.get(Q(email=identifier) | Q(username=identifier), password=passw)
            request.session['user'] = {
                    'username': user.username,
                    'email': user.email,
                    'password' : user.password,
                    'firstname': user.firstname,
                    'lastname': user.aboutuser
                }
            return redirect ('landing')
        except Users.DoesNotExist as e:
            print("Wala yung user")
            return render(request, 'quiz_up_app/signin.html')
    else:
        return render(request, 'quiz_up_app/signin.html')
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST or None)
        if form.is_valid():
            user = form.save()
            # Extract the password and confirm password from the POST data
            password = request.POST.get('password')
            confirmpass = request.POST.get('confirmpassword')

            # Check if the passwords match
            if password == confirmpass:
                # Print user details for debugging
                print(f"New user created: {user.username}, {user.email}")

                request.session['user'] = {
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'username': user.username,
                    'email': user.email,
                }

                return redirect('signin')
            else:
                # Print error message for debugging
                print("Passwords do not match.")
                return render(request, 'quiz_up_app/signup.html')

        else:
            # Print form errors for debugging
            print("Form is invalid:", form.errors)
            return render(request, 'quiz_up_app/signup.html')

    else:
        return render(request, 'quiz_up_app/signup.html')
