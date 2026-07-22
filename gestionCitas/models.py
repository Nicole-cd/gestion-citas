from django.db import models
from django.contrib.auth.models import AbstractUser

    # PARA CLIENTE, FREELANCER Y ADMIN  
class Usuario(AbstractUser):
    ROLES = (
        ('CLIENTE', 'Cliente'),
        ('FREELANCER', 'Freelancer'),
        ('ADMIN', 'Administrador'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='CLIENTE')
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})"


    # FREELANCER
class PerfilFreelancer(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_freelancer')
    especialidad = models.CharField(max_length=100)
    biografia = models.TextField(blank=True, null=True)
    horario_inicio = models.TimeField(help_text="Hora de inicio de jornada")
    horario_fin = models.TimeField(help_text="Hora de fin de jornada")
    tarifa_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Freelancer: {self.usuario.get_full_name()} - {self.especialidad}"


    # SERVICIOS
class Servicio(models.Model):
    freelancer = models.ForeignKey(PerfilFreelancer, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


    # CITA Reservar, CU-2: Cancelar, CU-4: Atender
class Cita(models.Model):
    ESTADOS = (
        ('RESERVADA', 'Reservada'),
        ('ATENDIDA', 'Atendida'),
        ('CANCELADA', 'Cancelada'),
    )
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='citas_cliente')
    freelancer = models.ForeignKey(PerfilFreelancer, on_delete=models.CASCADE, related_name='citas_freelancer')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='RESERVADA')
    motivo_cancelacion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cita #{self.id} - Cliente: {self.cliente} | Freelancer: {self.freelancer.usuario.first_name} ({self.estado})"


    # FACTURA
class Comprobante(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name='comprobante')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50, default='Efectivo/Transferencia')

    def __str__(self):
        return f"Comprobante Cita #{self.cita.id} - Total: ${self.monto}"


    # 6. HISTORIAL DE CAMBIOS DE ESTADO DE CITA
class HistorialCambio(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    usuario_responsable = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Historial Cita #{self.cita.id}: {self.estado_anterior} -> {self.estado_nuevo}"


    # 7. NOTIFICACIONES
class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario.username} - Leído: {self.leido}"
        