
from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    correo_cliente = models.EmailField(unique=True, max_length=30)
    contrasena = models.CharField(max_length=20)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Freelancer(models.Model):
    CATEGORIAS = [
        ('diseno_grafico', 'Diseño'),
        ('programacion', 'Programación'),
        ('musica', 'Música'),
        ('contabilidad', 'Contabilidad'),
        ('marketing_digital', 'Marketing Digital'),
        ('asesoria_legal', 'Asesoría Legal'),
    ]

    id_freelancer = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    correo = models.EmailField(unique=True, max_length=30)
    contrasena = models.CharField(max_length=20)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.get_categoria_display()}"

class Administrador(models.Model):
    id_administrador = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    correo = models.EmailField(unique=True, max_length=30)
    contrasena = models.CharField(max_length=20)
    fecha_registro = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    id_freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=30)
    descripcion = models.TextField(blank=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.IntegerField(help_text="Duración en minutos")
    modalidad = models.CharField(max_length=10, choices=[
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
        ('ambos', 'Ambos')
    ], default='ambos')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas')
    id_freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='reservas')
    id_servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    modalidad = models.CharField(max_length=10, choices=[
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual')
    ], default='virtual')
    estado = models.CharField(max_length=12, choices=[
        ('programada', 'Programada'),
        ('confirmada', 'Confirmada'),
        ('atendida', 'Atendida'),
        ('cancelada', 'Cancelada')
    ], default='programada')
    motivo_cancelacion = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.fecha}"

class Disponibilidad(models.Model):
    id_disponibilidad = models.AutoField(primary_key=True)
    id_freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.CharField(max_length=15, choices=[
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo')
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        unique_together = ['id_freelancer', 'dia_semana']

    def __str__(self):
        return f"{self.id_freelancer.nombre} - {self.dia_semana}"

class NoDisponibilidad(models.Model):
    id_no_disponible = models.AutoField(primary_key=True)
    id_freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='no_disponibilidades')
    fecha = models.DateField()
    motivo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ['id_freelancer', 'fecha']

    def __str__(self):
        return f"{self.id_freelancer.nombre} - {self.fecha}"


class HistorialCambio(models.Model):
    
    id_historial = models.AutoField(primary_key=True)
    
    administrador = models.ForeignKey(
        'Administrador', 
        on_delete=models.SET_NULL,  
        null=True,
        blank=True,
        related_name='historial_cambios'
    )
    
    ACCIONES = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('cancelar', 'Cancelar'),
        ('atender', 'Atender'),
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('reprogramar', 'Reprogramar'),
        ('confirmar', 'Confirmar'),
        ('rechazar', 'Rechazar'),
        ('activar', 'Activar'),
        ('desactivar', 'Desactivar'),
        ('exportar', 'Exportar'),
        ('importar', 'Importar'),
        ('resetear', 'Resetear'),
    ]
    
    accion = models.CharField(
        max_length=20,
        choices=ACCIONES,
        db_index=True,
        help_text="Tipo de acción realizada"
    )
    
    MODULOS = [
        ('Sistema', 'Sistema'),
        ('Citas', 'Citas'),
        ('Servicios', 'Servicios'),
        ('Freelancers', 'Freelancers'),
        ('Clientes', 'Clientes'),
        ('Administradores', 'Administradores'),
        ('Usuarios', 'Usuarios'),
        ('Reportes', 'Reportes'),
        ('Disponibilidad', 'Disponibilidad'),
        ('Pagos', 'Pagos'),
        ('Notificaciones', 'Notificaciones'),
        ('Perfil', 'Perfil'),
        ('Seguridad', 'Seguridad'),
    ]
    
    modulo = models.CharField(
        max_length=50,
        choices=MODULOS,
        db_index=True,
        help_text="Módulo del sistema afectado"
    )
    
    descripcion = models.TextField(
        max_length=500,
        help_text="Descripción detallada de la acción realizada"
    )
    
    registro_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID del registro afectado"
    )
    
    registro_nombre = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Nombre o descripción del registro afectado"
    )
    
    datos_anteriores = models.JSONField(
        null=True,
        blank=True,
        help_text="Datos anteriores del registro"
    )
    
    datos_nuevos = models.JSONField(
        null=True,
        blank=True,
        help_text="Datos nuevos del registro"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Dirección IP del usuario"
    )
    
    user_agent = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Navegador del usuario"
    )
    
    fecha_hora = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Fecha y hora del cambio"
    )
    
    def __str__(self):
        return f"{self.fecha_hora.strftime('%d/%m/%Y %H:%M')} - {self.get_accion_display()} - {self.modulo}"
    
    class Meta:
        verbose_name = "Historial de Cambio"
        verbose_name_plural = "Historial de Cambios"
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['fecha_hora']),
            models.Index(fields=['accion', 'modulo']),
        ]
    
    @classmethod
    def registrar(cls, administrador, accion, modulo, descripcion, 
                registro_id=None, registro_nombre=None, 
                datos_anteriores=None, datos_nuevos=None,
                ip_address=None, user_agent=None):

        return cls.objects.create(
            administrador=administrador,
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            registro_id=registro_id,
            registro_nombre=registro_nombre,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=ip_address,
            user_agent=user_agent,
            fecha_hora=timezone.now()
        )
    
