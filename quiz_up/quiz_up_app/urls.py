from . import views
from django.urls import path

urlpatterns =[
    path("", views.landing, name="landing"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("mainpage/", views.mainpage, name="mainpage"),
    path("dragfile/", views.dragfile, name="dragfile"),
    path("generatedquiz/", views.generatedquiz, name="generatedquiz"),
]