"""
Conexión a Supabase para YoCreo Suite
Gestiona usuarios via tabla suite_usuarios
"""

import logging
import streamlit as st
from supabase import create_client, Client

logger = logging.getLogger(__name__)

supabase: Client = None


def get_supabase() -> Client:
    """Obtiene el cliente de Supabase"""
    global supabase
    if supabase is None:
        supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_ANON_KEY"]
        )
    return supabase


def obtener_datos_usuario(email: str) -> dict | None:
    """
    Retorna el row completo de suite_usuarios para el email dado.
    Retorna None si no existe o no está activo.
    """
    try:
        client = get_supabase()
        response = client.table('suite_usuarios').select(
            'id, nombre, email, rol, plan, empresa, activo'
        ).eq('email', email.lower()).eq('activo', True).limit(1).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        logger.warning("Error obteniendo datos de usuario: %s", e)
        return None


def verificar_suscripcion(email: str) -> dict:
    """
    Verifica si un email tiene acceso activo en suite_usuarios.

    Retorna:
        {
            'tiene_suscripcion': bool,
            'status': str,  # 'active', 'none', 'error'
            'customer_id': str or None,
            'message': str
        }
    """
    try:
        usuario = obtener_datos_usuario(email)

        if usuario:
            return {
                'tiene_suscripcion': True,
                'status': 'active',
                'customer_id': usuario.get('id'),
                'message': 'Acceso autorizado'
            }
        else:
            return {
                'tiene_suscripcion': False,
                'status': 'none',
                'customer_id': None,
                'message': 'No se encontró suscripción para este email'
            }

    except Exception as e:
        logger.warning("Error verificando suscripción: %s", e)
        return {
            'tiene_suscripcion': False,
            'status': 'error',
            'customer_id': None,
            'message': f'Error de conexión: {str(e)}'
        }


def obtener_url_suscripcion() -> str:
    """Retorna la URL del landing para suscribirse"""
    return st.secrets.get("LANDING_URL", "https://yocreo-landing.vercel.app")


def registrar_uso_practica(email: str, practice_key: str, organization_id: str = None):
    """
    Registra el uso de una práctica en Supabase.

    Args:
        email: Email del usuario
        practice_key: Clave de la práctica (ej: 'priorizador_tareas')
        organization_id: ID de la organización (opcional)
    """
    try:
        client = get_supabase()
        data = {
            'email': email.lower(),
            'practice_key': practice_key
        }
        if organization_id:
            data['organization_id'] = organization_id

        client.table('practice_events').insert(data).execute()
    except Exception as e:
        # No interrumpir el flujo si falla el registro
        logger.warning("Error registrando uso de práctica: %s", e)
