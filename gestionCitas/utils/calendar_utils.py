from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_calendar_service():

    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def crear_evento_calendar(reserva):
    """
    Crea un evento en Google Calendar para la cita
    """
    try:
        service = get_google_calendar_service()
        
        # Preparar fechas
        fecha_inicio = datetime.datetime.combine(reserva.fecha, reserva.hora_inicio)
        fecha_fin = datetime.datetime.combine(reserva.fecha, reserva.hora_fin)
        
        # Crear el evento
        event = {
            'summary': f"Cita: {reserva.id_servicio.nombre}",
            'location': 'Virtual' if reserva.modalidad == 'virtual' else 'Presencial',
            'description': f"""
                Cliente: {reserva.id_cliente.nombre}
                Servicio: {reserva.id_servicio.nombre}
                Duración: {reserva.id_servicio.duracion} minutos
                Modalidad: {reserva.get_modalidad_display()}
                Código: RSV-{reserva.id_reserva:04d}
                
                Descripción del servicio:
                {reserva.id_servicio.descripcion or 'Sin descripción'}
                
                Contacto:
                Cliente: {reserva.id_cliente.correo_cliente}
                Freelancer: {reserva.id_freelancer.correo}
            """,
            'start': {
                'dateTime': fecha_inicio.isoformat(),
                'timeZone': 'America/Santo_Domingo',
            },
            'end': {
                'dateTime': fecha_fin.isoformat(),
                'timeZone': 'America/Santo_Domingo',
            },
            'attendees': [
                {'email': reserva.id_cliente.correo_cliente},
                {'email': reserva.id_freelancer.correo},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
    
        event = service.events().insert(calendarId='primary', body=event).execute()
        
        return event.get('htmlLink')
        
    except Exception as e:
        print(f"Error al crear evento en Google Calendar: {e}")
        return None

def eliminar_evento_calendar(evento_id):
    try:
        service = get_google_calendar_service()
        service.events().delete(calendarId='primary', eventId=evento_id).execute()
        return True
    except Exception as e:
        print(f"Error al eliminar evento: {e}")
        return False