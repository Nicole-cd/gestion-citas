from django.urls import path
from . import views

urlpatterns = [    
    path('historial/', views.historial_cambios, name='historial_cambios'),
]