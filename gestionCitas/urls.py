from django.urls import path
from . import views

urlpatterns = [
    # autenticación
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),

    # cliente
    path('cliente/', views.cliente_dashboard, name='cliente_dashboard'),
    path('cliente/reservar/', views.reservar_cita, name='reservar_cita'),
    path('cliente/mis-citas/', views.mis_citas, name='mis_citas'),
    path('cliente/citas/<int:pk>/cancelar/', views.cancelar_cita, name='cancelar_cita'),

    # freelancer
    path('freelancer/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('freelancer/servicios/', views.registrar_servicio, name='registrar_servicio'),
    path('freelancer/disponibilidad/', views.disponibilidad_view, name='disponibilidad'),
    path('freelancer/citas/<int:pk>/atender/', views.atender_cita, name='atender_cita'),

    # admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    path('admin-panel/reportes/', views.reportes_view, name='reportes'),
    path('admin-panel/freelancers/', views.listado_freelancers_view, name='listado_freelancers'),



]
