from datetime import date
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, Q

from .models import (
    Cliente, Freelancer, Administrador, Servicio, Reserva,
    Disponibilidad, NoDisponibilidad, HistorialCambio, Notificacion,
)
# Create your views here.
def rol_actual(request):
    return request.session.get("rol")

def requiere_rol(*roles):

    def decorador(vista):
        def envoltura(request, *args, **kwargs):
            if rol_actual(request) not in roles:
                messages.error(request, "Desbes de iniciar sesión para continuar")
                return redirect("login")
                return vista(request, *args, **kwargs)
            return envoltura
        return decorador
    


def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo", "").strip()
        password = request.POST.get("password", "")

        for modelo, rol, compo_correo in [
            (Cliente,"cliente", "correo_cliente"),
            (Freelancer, "freelancer", "correo"),
            (Administrador, "administrador", "correo"),
        ]:
            usuario = modelo.objects.filter(**{campo_correo: correo}).first()
            if usuario and check_password(password, usuario.contrasena):
                request.session["rol"] = rol
                request.session["user_id"] = usuario.pk
                request.session["nombre"] = usuario.nombre
                destino = {
                    "cliente": "cliente_dashboard",
                    "freelancer": "freelancer_dashboard",
                    "administrador": "admin_dashboard",
                }[rol]
                return redirect(destino)
            
        messages.error(request, "correo o contraseña incorrectos.")

    return render(request, "templates/login.html")

def logout_view(request):
    request.session.flush()
    return redirect("login")

def registro_view(request):
    if request.method == "POST":
        nombre =  request.POST.get("nombre", "").strip()
        correo =  request.POST.get("correo", "").strip()
        password = make_password(request.POST.get("password", ""))
        rol =  request.POST.get("rol")

        if rol == "cliente":
            Cliente.objects.create(nombre=nombre, correo_cliente=correo, contrasena=password )
        elif rol == "freelancer":
            Freelancer.objects.create(
            nombre=nombre, correo=correo, contrasena=password, categoria=request.POST.get("categoria", ""),
        )
        elif rol == 'administrador':
            Administrador.objects.create(nombre=nombre, correo=correo, contrasena=password)
        else:
            messages.error(request, "Selecciona un rol válido.")
            return render(request, "templates/registro.html")
    
    return render(request, "templates/registro.html")

@requiere_rol("cliente")
def cliente_dashboard(request):
    freelancers = Freelancer.objects.annotate(servicios_count=Count("servicios"))
    proxima_citas = (
        Reserva.objects.filter(id_cliente_id=request.session["user_id"], estado="programada")
        .select_related("id_freelancer", "id_servicio")
        .order_by("fecha", "hora_inicio")
        .first()
    )
    return render(request, "templates/cliente/dashboard.html", {
        "freelancers": freelancers,
        "proxima_cita": proxima_citas,
    })

@requiere_rol("cliente")
def reservar_cita(request):
    freelancers = Freelancer.objects.all()

    if request.method == "POST":
        freelancer_id = request.POST["freelancer"]
        servicio = get_object_or_404(Servicio, pk=request.POST["servicio"])
        fecha = request.POST["fecha"]
        hora = request.POST["hora"]

        conflicto = Reserva.objects.filter(
            id_freelancer_id=freelancer_id,  fecha=fecha, hora_inicio=hora,
        ).exclude(estado="cancelada").exists()

        if conflicto:
            messages.error(request, "El horario ya no está disponible. Elige otro horario.")
        else:
            Reserva.objects.create(
                id_cliente_id=request.session["user_id"],
                id_freelancer_id=freelancer_id,
                id_servicio=servicio,
                fecha=fecha,
                hora_inicio=hora,
                hora_fin=hora,  # ajustar sumando la duración del servicio
                modalidad=request.POST["modalidad"],
            )
            messages.success(request, "Cita reservada.")
            return redirect("mis_citas")

    return render(request, "templates/cliente/reservar_cita.html", {"freelancers": freelancers})


@requiere_rol("cliente")
def mis_citas(request):
    citas = (
        Reserva.objects.filter(id_cliente_id=request.session["user_id"])
        .select_related("id_freelancer", "id_servicio")
        .order_by("-fecha")
    )
    return render(render, "templates/cliente/mis-citas.html", {"citas": citas})


@requiere_rol("cliente")
def cancelar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk, id_cliente_id=request.session["user_id"])
    if request.method == "POST":
        cita.estado = "cancelada"
        cita.motivo_cancelacion = request.POST.get("motivo", "")
        cita.save()
        messages.success(request, "Cita cancelada con éxito.")
    return redirect("mis_citas")


@requiere_rol("freelancer")
def freelancer_dashboard(request):
    citas_hoy = (
        Reserva.objects.filter(id_freelancer_id=request.session["user_id"], fecha=date.today())
        .select_related("id_cliente", "id_servicio")
        .order_by("hora_inicio")
    )
    return render(request, "templates/freelancer/dashboard.html", {
        "citas_hoy": citas_hoy,
        "citas_hoy_count": citas_hoy.count(),
    })

@requiere_rol("freelancer")
def registrar_servicio(request):
    if request.method == "POST":
        Servicio.objects.create(
            id_freelancer_id=request.session["user_id"],
            nombre=request.POST["nombre"],
            descripcion=request.POST.get("detalle", ""),
            precio_base=request.POST["precio_base"],
            duracion=request.POST["duracion"],
            modalidad=request.POST["modalidad"],
        )
        messages.success(request, "Servicio guardado.")
        return redirect(request, "templates/freelancer/registrar_servicio.html", {"servicios": Servicio})
    


@requiere_rol("freelancer")
def disponibilidad(request):
    freelancer_id = request.session["user_id"]

    if request.method == "POST":
        if "fecha_no_disponible" in request.POST:
            NoDisponibilidad.objects.create(
                id_freelancer_id=freelancer_id,
                fecha=request.POST["fecha_no_disponible"],
            )
        else:
            for dia in ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]:
                if request.POST.get(f"{dia}_activo"):
                    Disponibilidad.objects.unpdate_or_create(
                        id_freelancer_id=freelancer_id, dia_semana=dia,
                        defaults={
                            "hora_inicio": request.POST[f"{dia}_inicio"],
                            "hora_fin": request.POST[f"{dia}_fin"],
                        },
                    )
        messages.success(request, "Disponibilidad actualizada.")

        ausencias = NoDisponibilidad.objects.filter(id_freelancer_id=freelancer_id).order_by("fecha")
        return render(request, "templates/freelancer/disponibilidad.html", {"ausencias": ausencias})
    

@requiere_rol("administrador")
def reportes(request):
    tipo = request.GET.get("tipo", "citas")
    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")

    filas = Reserva.objects.select_related("id_cliente", "id_freelancer", "id_servicio")
    if desde:
        filas = filas.filter(fecha__gte=desde)
    if hasta:
        filas = filas.filter(fecha__gte=hasta)
    
    return render(request, "templates/admin/reportes.html", {
        "tipo": tipo, "desde":desde, "hasta": hasta,
        "filas": filas,
        "total_citas": filas.count(),
        "total_ingresos": filas.filter(estado="atendida").aggregate(
            total=Sum("id_servicio__precio_base")
        )["total"] or 0,
    })

@requiere_rol("administrador")
def historial_cambios(request):
    historial = HistorialCambio.objects.select_related("administrador")
    admin_filtro = request.GET.get("administrador")
    if admin_filtro:
        historial = historial.filter(administrador_id=admin_filtro)
    return render(request, "templates/admin/historial_cambios.html", {"historial": historial})

@requiere_rol("administrador")
def listado_freelancers(request):
    freelancers = Freelancer.objects.annotate(cant_servicios=Count("servicios"))
    return render(request, "templates/admin/listado_freelancers.html", {
        "freelancers": freelancers,
        "total_freelancers": freelancers.count(),
    })


