"""
Tokens de sesión persistente — YoCreo Suite
HMAC-SHA256 guardados en browser localStorage. TTL: 7 días.
"""
import hmac
import hashlib
import base64
import time
import logging
import streamlit as st

logger = logging.getLogger(__name__)
TOKEN_TTL_SECS = 7 * 24 * 3600   # 7 días


def _secret() -> bytes:
    key = st.secrets.get("SESSION_SECRET", "") or st.secrets.get("SUPABASE_ANON_KEY", "")
    return (key or "yocreo_suite_key_2024").encode()


def generar_token(email: str) -> str:
    """Genera un token firmado con HMAC-SHA256 para el email dado."""
    expires = int(time.time()) + TOKEN_TTL_SECS
    payload = f"{email}:{expires}"
    sig = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
    raw = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def validar_token(token: str) -> str:
    """Retorna el email si el token es válido y no expiró. Retorna '' si no."""
    try:
        padded = token + "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(padded.encode()).decode()
        parts = raw.split(":")
        if len(parts) != 3:
            return ""
        email, expires_str, sig = parts
        payload = f"{email}:{expires_str}"
        expected = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return ""
        if time.time() > int(expires_str):
            return ""
        return email
    except Exception as e:
        logger.debug("Token inválido: %s", e)
        return ""
