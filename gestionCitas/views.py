from datetime import date, datetime, timedelta
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum
from .models import Cliente, Freelancer, Administrador, Servicio, Reserva, Disponibilidad, NoDisponibilidad
from .models import HistorialCambio, Administrador
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings

#general
def get_rol(request):
    return request.session.get('rol')

def requiere_rol(*roles):

    def decorador(vista):
        def wrapper(request, *args, **kwargs):

            if 'rol' not in request.session:
                messages.error(request, "Debes iniciar sesión para continuar.")
                return redirect('login')

            if request.session.get('rol') not in roles:
                messages.error(request, "No tienes permiso para acceder a esta sección.")
                return redirect('login')

            return vista(request, *args, **kwargs)
        return wrapper
    return decorador

def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        password = request.POST.get('password', '')

        cliente = Cliente.objects.filter(correo_cliente=correo).first()
        if cliente and check_password(password, cliente.contrasena):
            request.session['rol'] = 'cliente'
            request.session['user_id'] = cliente.id_cliente
            request.session['nombre'] = cliente.nombre
            return redirect('cliente_dashboard')

        freelancer = Freelancer.objects.filter(correo=correo).first()
        if freelancer and check_password(password, freelancer.contrasena):
            request.session['rol'] = 'freelancer'
            request.session['user_id'] = freelancer.id_freelancer
            request.session['nombre'] = freelancer.nombre
            return redirect('freelancer_dashboard')

        admin = Administrador.objects.filter(correo=correo).first()
        if admin and check_password(password, admin.contrasena):
            request.session['rol'] = 'administrador'
            request.session['user_id'] = admin.id_administrador
            request.session['nombre'] = admin.nombre
            return redirect('admin_dashboard')

        messages.error(request, "Correo o contraseña incorrectos.")

    return render(request, 'citas/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def registro_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        correo = request.POST.get('correo', '').strip()
        password = make_password(request.POST.get('password', ''))
        rol = request.POST.get('rol')

        if rol == 'cliente':
            Cliente.objects.create(
                nombre=nombre,
                correo_cliente=correo,
                contrasena=password
            )
            messages.success(request, "Cuenta de cliente creada exitosamente.")
            return redirect('login')
        elif rol == 'freelancer':
            freelancer = Freelancer.objects.create(
                nombre=nombre,
                correo=correo,
                contrasena=password,
                categoria=request.POST.get('categoria', '')
            )

            dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']
            for dia in dias:
                Disponibilidad.objects.create(
                    id_freelancer=freelancer,
                    dia_semana=dia,
                    hora_inicio='09:00',
                    hora_fin='17:00'
                )
            messages.success(request, "Cuenta de freelancer creada exitosamente.")
            return redirect('login')
        else:
            messages.error(request, "Selecciona un rol válido.")

    return render(request, 'citas/registro.html')

#cliente

@requiere_rol('cliente')
def cliente_dashboard(request):
    freelancers = Freelancer.objects.filter(activo=True).annotate(
        servicios_count=Count('servicios')
    )
    proxima_cita = Reserva.objects.filter(
        id_cliente_id=request.session['user_id'],
        estado='programada'
    ).select_related('id_freelancer', 'id_servicio').order_by('fecha', 'hora_inicio').first()

    return render(request, 'citas/cliente/dashboard.html', {
        'freelancers': freelancers,
        'proxima_cita': proxima_cita,
    })

@requiere_rol('cliente')
def reservar_cita(request):
    freelancers = Freelancer.objects.filter(activo=True)
    todos_servicios = Servicio.objects.filter(activo=True).select_related('id_freelancer')
    
    if request.method == 'POST':
        freelancer_id = request.POST.get('freelancer')
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        modalidad = request.POST.get('modalidad')

        if not all([freelancer_id, servicio_id, fecha, hora, modalidad]):
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'citas/cliente/reservar_cita.html', {
                'freelancers': freelancers,
                'todos_servicios': todos_servicios
            })

        servicio = get_object_or_404(Servicio, pk=servicio_id, activo=True)

        conflicto = Reserva.objects.filter(
            id_freelancer_id=freelancer_id,
            fecha=fecha,
            hora_inicio=hora,
        ).exclude(estado='cancelada').exists()

        if conflicto:
            messages.error(request, "El horario ya no está disponible. Elige otro horario.")
            return render(request, 'citas/cliente/reservar_cita.html', {
                'freelancers': freelancers,
                'todos_servicios': todos_servicios
            })

        hora_inicio = datetime.strptime(hora, '%H:%M').time()
        hora_fin_dt = datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=servicio.duracion)
        hora_fin = hora_fin_dt.time()

        reserva = Reserva.objects.create(
            id_cliente_id=request.session['user_id'],
            id_freelancer_id=freelancer_id,
            id_servicio=servicio,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            modalidad=modalidad,
            estado='programada'
        )

        try:
            cliente = reserva.id_cliente
            freelancer = reserva.id_freelancer  
            servicio = reserva.id_servicio

            fecha_str = str(reserva.fecha)
            hora_str = str(reserva.hora_inicio)
        
            print(f"Cliente: {cliente.nombre} - {cliente.correo_cliente}")
            print(f"Freelancer: {freelancer.nombre} - {freelancer.correo}")
            

            mensaje = f"""
            Hola {cliente.nombre},
            
            Tu cita ha sido confirmada exitosamente.
            
            Detalles:
            - Servicio: {servicio.nombre}
            - Profesional: {freelancer.nombre}
            - Fecha: {fecha_str}
            - Hora: {hora_str}
            - Modalidad: {reserva.get_modalidad_display()}
            
            ¡Gracias por usar nuestro servicio!
            """

            send_mail(
                subject=f'Cita confirmada - {servicio.nombre}',
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cliente.correo_cliente],
                fail_silently=False,
            )
            
            send_mail(
                subject=f'Nueva cita - {servicio.nombre}',
                message=f"Hola {freelancer.nombre},\n\nTienes una nueva cita:\n\n{cliente.nombre} ha reservado {servicio.nombre} para el {fecha_str} a las {hora_str}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[freelancer.correo],
                fail_silently=False,
            )
            
            print("correo enviado exitosamente.")
            messages.success(request, "Cita reservada exitosamente. Revisa tu correo para los detalles.")
            
        except Exception as e:
            print(f" Error al enviar correo: {e}")
            import traceback
            traceback.print_exc()
            messages.warning(request, f"Cita reservada, pero hubo un problema al enviar el correo.")

        return redirect('mis_citas')

    return render(request, 'citas/cliente/reservar_cita.html', {
        'freelancers': freelancers,
        'todos_servicios': todos_servicios
    })


@requiere_rol('cliente')
def mis_citas(request):
    citas = Reserva.objects.filter(
        id_cliente_id=request.session['user_id']
    ).select_related('id_freelancer', 'id_servicio').order_by('-fecha')

    return render(request, 'citas/cliente/mis_citas.html', {'citas': citas})

@requiere_rol('cliente')
def cancelar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk, id_cliente_id=request.session['user_id'])

    if request.method == 'POST':
        cita.estado = 'cancelada'
        cita.motivo_cancelacion = request.POST.get('motivo', '')
        cita.save()

        messages.success(request, "Cita cancelada exitosamente.")
        return redirect('mis_citas')

    return render(request, 'citas/cliente/cancelar_cita.html', {'cita': cita})

#freelancer

@requiere_rol('freelancer')
def freelancer_dashboard(request):
    hoy = date.today()
    citas_hoy = Reserva.objects.filter(
        id_freelancer_id=request.session['user_id'],
        fecha=hoy,
        estado__in=['programada', 'confirmada']
    ).select_related('id_cliente', 'id_servicio').order_by('hora_inicio')

    proximas_citas = Reserva.objects.filter(
        id_freelancer_id=request.session['user_id'],
        fecha__gte=hoy,
        estado__in=['programada', 'confirmada']
    ).select_related('id_cliente', 'id_servicio').order_by('fecha', 'hora_inicio')[:10]

    return render(request, 'citas/freelancer/dashboard.html', {
        'citas_hoy': citas_hoy,
        'citas_hoy_count': citas_hoy.count(),
        'proximas_citas': proximas_citas,
    })

@requiere_rol('freelancer')
def atender_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk, id_freelancer_id=request.session['user_id'])

    if request.method == 'POST':
        cita.estado = 'atendida'
        cita.observaciones = request.POST.get('observaciones', '')
        cita.save()
        messages.success(request, "Servicio finalizado exitosamente.")
        return redirect('freelancer_dashboard')

    return render(request, 'citas/freelancer/atender_cita.html', {'cita': cita})

@requiere_rol('freelancer')
def registrar_servicio(request):
    freelancer_id = request.session['user_id']
    servicios = Servicio.objects.filter(id_freelancer_id=freelancer_id)

    if request.method == 'POST':
        Servicio.objects.create(
            id_freelancer_id=freelancer_id,
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion', ''),
            precio_base=request.POST.get('precio_base'),
            duracion=request.POST.get('duracion'),
            modalidad=request.POST.get('modalidad', 'ambos'),
        )
        messages.success(request, "Servicio guardado exitosamente.")
        return redirect('registrar_servicio')

    return render(request, 'citas/freelancer/registrar_servicio.html', {'servicios': servicios})

@requiere_rol('freelancer')
def disponibilidad_view(request):
    freelancer_id = request.session['user_id']

    if request.method == 'POST':
        if 'fecha_no_disponible' in request.POST:
            NoDisponibilidad.objects.create(
                id_freelancer_id=freelancer_id,
                fecha=request.POST.get('fecha_no_disponible'),
                motivo=request.POST.get('motivo_no_disponible', '')
            )
            messages.success(request, "Día no disponible agregado.")
        else:
            dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
            for dia in dias:
                if request.POST.get(f'{dia}_activo'):
                    Disponibilidad.objects.update_or_create(
                        id_freelancer_id=freelancer_id,
                        dia_semana=dia,
                        defaults={
                            'hora_inicio': request.POST.get(f'{dia}_inicio', '09:00'),
                            'hora_fin': request.POST.get(f'{dia}_fin', '17:00'),
                        }
                    )
                else:
                    Disponibilidad.objects.filter(
                        id_freelancer_id=freelancer_id,
                        dia_semana=dia
                    ).delete()
            messages.success(request, "Disponibilidad actualizada.")

    disponibilidades = Disponibilidad.objects.filter(id_freelancer_id=freelancer_id)
    ausencias = NoDisponibilidad.objects.filter(id_freelancer_id=freelancer_id).order_by('fecha')

    return render(request, 'citas/freelancer/disponibilidad.html', {
        'disponibilidades': disponibilidades,
        'ausencias': ausencias,
    })

#admin

@requiere_rol('administrador')
def admin_dashboard(request):
    total_clientes = Cliente.objects.count()
    total_freelancers = Freelancer.objects.count()
    total_servicios = Servicio.objects.count()
    citas_hoy = Reserva.objects.filter(fecha=date.today()).count()
    citas_pendientes = Reserva.objects.filter(estado='programada').count()
    return render(request, 'citas/admin/dashboard.html', {
        'total_clientes': total_clientes,
        'total_freelancers': total_freelancers,
        'total_servicios': total_servicios,
        'citas_hoy': citas_hoy,
        'citas_pendientes': citas_pendientes,
    })

@requiere_rol('administrador')
def reportes_view(request):
    tipo = request.GET.get('tipo', 'citas')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    reservas = Reserva.objects.select_related('id_cliente', 'id_freelancer', 'id_servicio')
    if desde:
        reservas = reservas.filter(fecha__gte=desde)
    if hasta:
        reservas = reservas.filter(fecha__lte=hasta)
    total_citas = reservas.count()
    total_ingresos = reservas.filter(estado='atendida').aggregate(
        total=Sum('id_servicio__precio_base')
    )['total'] or 0

    return render(request, 'citas/admin/reportes.html', {
        'tipo': tipo,
        'desde': desde,
        'hasta': hasta,
        'reservas': reservas,
        'total_citas': total_citas,
        'total_ingresos': total_ingresos,
    })

@requiere_rol('administrador')
def historial_cambios_view(request):
    historial = HistorialCambio.objects.select_related('administrador').order_by('-fecha_hora')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    accion = request.GET.get('accion', '')
    
    if desde:
        try:
            historial = historial.filter(fecha_hora__date__gte=desde)
        except:
            pass
    if hasta:
        try:
            historial = historial.filter(fecha_hora__date__lte=hasta)
        except:
            pass

    if accion:
        historial = historial.filter(accion__icontains=accion)
    total_cambios = historial.count()
    paginator = Paginator(historial, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'historial': page_obj,
        'total_cambios': total_cambios,
        'desde': desde,
        'hasta': hasta,
        'accion': accion,
    }
    return render(request, 'citas/admin/historial_cambios.html', context)

@requiere_rol('administrador')
def crear_admin(request):

    administradores = Administrador.objects.all().order_by('-fecha_registro')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        correo = request.POST.get('correo', '').strip()
        password = request.POST.get('password', '')
        
        if not nombre or not correo or not password:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'citas/admin/crear_admin.html', {
                'administradores': administradores
            })
        
        if len(password) < 6:
            messages.error(request, "La contraseña debe tener al menos 6 caracteres.")
            return render(request, 'citas/admin/crear_admin.html', {
                'administradores': administradores
            })
        if Administrador.objects.filter(correo=correo).exists():
            messages.error(request, f"El correo {correo} ya está registrado como administrador.")
            return render(request, 'citas/admin/crear_admin.html', {
                'administradores': administradores
            })
        from .models import Cliente, Freelancer
        if Cliente.objects.filter(correo_cliente=correo).exists():
            messages.error(request, f"El correo {correo} ya está registrado como cliente.")
            return render(request, 'citas/admin/crear_admin.html', {
                'administradores': administradores
            })
        if Freelancer.objects.filter(correo=correo).exists():
            messages.error(request, f"El correo {correo} ya está registrado como freelancer.")
            return render(request, 'citas/admin/crear_admin.html', {
                'administradores': administradores
            })
        
        from django.contrib.auth.hashers import make_password
        Administrador.objects.create(
            nombre=nombre,
            correo=correo,
            contrasena=make_password(password)
        )
        messages.success(request, f"Administrador {nombre} creado exitosamente.")
        return redirect('admin_dashboard')
    return render(request, 'citas/admin/crear_admin.html', {
        'administradores': administradores
    })

@requiere_rol('administrador')
def listado_freelancers_view(request):
    freelancers = Freelancer.objects.annotate(
        servicios_count=Count('servicios')
    ).order_by('-fecha_registro')
    
    total_freelancers = freelancers.count()
    
    from django.core.paginator import Paginator
    paginator = Paginator(freelancers, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'citas/admin/listado_freelancers.html', {
        'freelancers': page_obj,
        'total_freelancers': total_freelancers,

    })