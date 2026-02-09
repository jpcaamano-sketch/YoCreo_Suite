"""
Helper para registrar uso de prácticas en Analytics
"""

import logging
import streamlit as st
from .database import registrar_uso_practica

logger = logging.getLogger(__name__)


def registrar_uso(practice_key: str):
    """
    Registra el uso de una práctica para el usuario actual.
    Debe llamarse cuando se genera contenido exitosamente.

    Args:
        practice_key: Clave de la práctica (ej: 'priorizador_tareas')
    """
    try:
        user = st.session_state.get('user')
        user_role = st.session_state.get('user_role', {})

        if user and user.get('email'):
            email = user['email']
            organization_id = user_role.get('organization_id')
            registrar_uso_practica(email, practice_key, organization_id)
    except Exception as e:
        # No interrumpir el flujo si falla el registro
        logger.warning("Error en registrar_uso: %s", e)
