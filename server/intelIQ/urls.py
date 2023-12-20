from django.urls import path
from .views import welcome
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('welcome/', welcome, name='welcome'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)