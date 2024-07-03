from django.contrib import admin
from django.urls import path, include
from theme.views import change_theme

urlpatterns = [
    path('admin/', admin.site.urls),
    path('switch-theme/', change_theme, name="change-theme"),
    path('', include("quiz_up_app.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    
]
