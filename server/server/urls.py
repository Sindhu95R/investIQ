from django.contrib import admin
from django.urls import path, include
from intelIQ.views import Index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('intelIQ/', include('intelIQ.urls')),
    path('post/', include('intelIQ.api.urls')),
]
