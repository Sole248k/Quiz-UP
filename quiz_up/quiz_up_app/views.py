from django.shortcuts import render

# Create your views here.
def landing(request):
    context={}
    return render(request, "quiz_up_app/landing.html", context)