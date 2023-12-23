from django.urls import path

from .import views

urlpatterns = [
    path('',views.Index, name='index'),
    # path('intelIQ/', include('intelIQ.urls'))
    # path('<str:room_name>', views.room, name='intelIQ'),
]