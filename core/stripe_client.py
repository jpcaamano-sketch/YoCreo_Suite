"""
Cliente Stripe para YoCreo Suite
Genera sesiones del Customer Portal para gestión de suscripción.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)


def crear_portal_session(customer_id: str, return_url: str) -> str | None:
    """
    Genera URL del Stripe Customer Portal para que el usuario gestione
    su suscripción (cancelar, cambiar método de pago, ver historial).

    Requiere STRIPE_SECRET_KEY en secrets.toml.
    Retorna la URL o None si falla.
    """
    try:
        import stripe
        stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", "")
        if not stripe.api_key or stripe.api_key.startswith("sk_REEMPLAZA"):
            logger.warning("STRIPE_SECRET_KEY no configurada en secrets.toml")
            return None
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session.url
    except Exception as e:
        logger.warning("Error creando sesión portal Stripe: %s", e)
        return None


def actualizar_seats_empresa(organization_id: str, nueva_cantidad: int) -> bool:
    """
    Llama al endpoint /api/update-seats del landing para actualizar
    la cantidad de asientos en Stripe cuando el admin agrega/elimina miembros.

    Requiere LANDING_API_URL y LANDING_API_KEY en secrets.toml.
    Retorna True si tuvo éxito.
    """
    try:
        import requests
        landing_url = st.secrets.get("LANDING_API_URL", "").rstrip("/")
        api_key     = st.secrets.get("LANDING_API_KEY", "")
        if not landing_url or not api_key:
            logger.warning("LANDING_API_URL o LANDING_API_KEY no configurados — omitiendo sync Stripe seats")
            return False

        resp = requests.post(
            f"{landing_url}/api/update-seats",
            json={
                "organization_id": organization_id,
                "new_quantity":    nueva_cantidad,
                "api_key":         api_key,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return True
        logger.warning("update-seats respondió %s: %s", resp.status_code, resp.text)
        return False
    except Exception as e:
        logger.warning("Error llamando update-seats: %s", e)
        return False
