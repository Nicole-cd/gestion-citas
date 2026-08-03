from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def enviar_correo_notificacion(reserva, tipo='confirmacion'):
    
    try:
        cliente = reserva.id_cliente
        freelancer = reserva.id_freelancer
        servicio = reserva.id_servicio
        
        asuntos = {
            'confirmacion': f'Cita confirmada - {servicio.nombre}',
            'recordatorio': f'Recordatorio de cita - {servicio.nombre}',
            'cancelacion': f'Cita cancelada - {servicio.nombre}',
            'modificacion': f'Cita modificada - {servicio.nombre}',
        }
        
        asunto = asuntos.get(tipo, 'Notificación de cita')
        
        context = {
            'cliente_nombre': cliente.nombre,
            'freelancer_nombre': freelancer.nombre,
            'servicio_nombre': servicio.nombre,
            'servicio_descripcion': servicio.descripcion,
            'fecha': reserva.fecha.strftime('%d/%m/%Y'),
            'hora': reserva.hora_inicio.strftime('%H:%M'),
            'hora_fin': reserva.hora_fin.strftime('%H:%M'),
            'modalidad': reserva.get_modalidad_display(),
            'precio': f"RD$ {servicio.precio_base}",
            'duracion': f"{servicio.duracion} minutos",
            'tipo': tipo,
            'codigo_reserva': f"RSV-{reserva.id_reserva:04d}",
            'enlace_google_calendar': generar_enlace_google_calendar(reserva),
        }
        
        html_content = render_to_string('citas/emails/notificacion_cita.html', context)
        text_content = strip_tags(html_content)
        
        send_mail(
            subject=asunto,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.correo_cliente],
            html_message=html_content,
            fail_silently=False,
        )
        
        send_mail(
            subject=f"Nueva cita - {servicio.nombre}",
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[freelancer.correo],
            html_message=html_content,
            fail_silently=False,
        )
        
        logger.info(f"Correo enviado para reserva {reserva.id_reserva}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar correo: {e}")
        return False

def generar_enlace_google_calendar(reserva):
    
    from datetime import datetime
    
    fecha_inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
    fecha_fin = datetime.combine(reserva.fecha, reserva.hora_fin)
    
    
    start = fecha_inicio.strftime('%Y%m%dT%H%M%S')
    end = fecha_fin.strftime('%Y%m%dT%H%M%S')
    
    text = f"Cita: {reserva.id_servicio.nombre} con {reserva.id_freelancer.nombre}"
    
    url = f"https://www.google.com/calendar/render?action=TEMPLATE&text={text}&dates={start}/{end}&details={reserva.id_servicio.descripcion}&location={reserva.modalidad}"
    
    return url