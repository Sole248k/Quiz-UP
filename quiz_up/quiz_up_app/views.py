from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def landing(request):
    context={}
    return render(request, "quiz_up_app/landing.html", context)

def signin(request):
    if request.method == 'POST':
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = Users.objects.get(username=username)
            if check_password(password, user.password):
            
                request.session['user_id'] = user.id
                return redirect('dashboard')  # Redirect to dashboard or any other page
            else:
                # Password is incorrect
                return render(request, 'quiz_up_app/signin.html', {'error': 'Invalid username or password'})
        except Users.DoesNotExist:
            # User does not exist
            return render(request, 'quiz_up_app/signin.html', {'error': 'User does not exist'})
    
   
    return render(request, 'quiz_up_app/signin.html')