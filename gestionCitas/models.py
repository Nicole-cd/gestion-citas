from django.db import models

class Freelancer(models.Model):
    # IDENTIFICACION
    id_freelancer = models.AutoField(primary_key=True)
    
    # DATOS DE ACCESO
    correo = models.EmailField(unique=True, max_length=150)
    contrasena = models.CharField(max_length=255)
    
    # PERFIL PUBLICO
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    especialidad = models.CharField(max_length=100)
    
    # CONTROL SISTEMA  
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.especialidad}"
