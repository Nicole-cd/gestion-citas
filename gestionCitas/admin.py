from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilFreelancer, Servicio, Cita, Comprobante, HistorialCambio, Notificacion

admin.site.register(Usuario, UserAdmin)
admin.site.register(PerfilFreelancer)
admin.site.register(Servicio)
admin.site.register(Cita)
admin.site.register(Comprobante)
admin.site.register(HistorialCambio)
admin.site.register(Notificacion)
