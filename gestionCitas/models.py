
from django.db import models

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    correo_cliente = models.EmailField(unique=True, max_length=30)
    contrasena = models.CharField(max_length=20)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Freelancer(models.Model):
    id_freelancer = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    correo = models.EmailField(unique=True, max_length=30)
    contrasena = models.CharField(max_length=20)
    categoria = models.CharField(max_length=15, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.categoria}"

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
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE, related_name='historial_cambios')
    accion = models.CharField(max_length=10)
    modulo = models.CharField(max_length=15)
    descripcion = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accion} - {self.fecha_hora}"
