"""
Conexión a Supabase para YoCreo Suite
Verifica suscripciones pagadas a través del landing
"""

from supabase import create_client, Client
import os

# Credenciales de Supabase (mismas que el landing)
SUPABASE_URL = "https://efomzdzxkwfmzbturvat.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmb216ZHp4a3dmbXpidHVydmF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3NDg1NDIsImV4cCI6MjA4NDMyNDU0Mn0.j0XDhxsBhZpcQ4sGjKLPvbmcMKHxalzfAp7qOdywYQQ"

# URL del landing para suscribirse
LANDING_URL = "https://yocreo-landing.vercel.app"

supabase: Client = None


def get_supabase() -> Client:
    """Obtiene el cliente de Supabase"""
    global supabase
    if supabase is None:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return supabase


def verificar_suscripcion(email: str) -> dict:
    """
    Verifica si un email tiene suscripción activa en Supabase.

    Retorna:
        {
            'tiene_suscripcion': bool,
            'status': str,  # 'active', 'canceled', 'trial', 'none'
            'customer_id': str or None,
            'message': str
        }
    """
    try:
        client = get_supabase()

        # Buscar suscripción por email
        response = client.table('subscriptions').select('*').eq('email', email.lower()).execute()

        if response.data and len(response.data) > 0:
            subscription = response.data[0]
            status = subscription.get('status', 'unknown')

            if status == 'active':
                return {
                    'tiene_suscripcion': True,
                    'status': 'active',
                    'customer_id': subscription.get('customer_id'),
                    'message': 'Suscripción activa'
                }
            elif status == 'trialing':
                return {
                    'tiene_suscripcion': True,
                    'status': 'trial',
                    'customer_id': subscription.get('customer_id'),
                    'message': 'Período de prueba activo'
                }
            else:
                return {
                    'tiene_suscripcion': False,
                    'status': status,
                    'customer_id': subscription.get('customer_id'),
                    'message': f'Suscripción {status}'
                }
        else:
            return {
                'tiene_suscripcion': False,
                'status': 'none',
                'customer_id': None,
                'message': 'No se encontró suscripción para este email'
            }

    except Exception as e:
        print(f"Error verificando suscripción: {e}")
        return {
            'tiene_suscripcion': False,
            'status': 'error',
            'customer_id': None,
            'message': f'Error de conexión: {str(e)}'
        }


def obtener_url_suscripcion() -> str:
    """Retorna la URL del landing para suscribirse"""
    return LANDING_URL
