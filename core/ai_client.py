"""
Cliente de IA para YoCreo Suite
Protocolo: gemini-2.5-flash
"""

import json
import time
import logging
import streamlit as st
import google.generativeai as genai
from .config import AI_CONFIG

logger = logging.getLogger(__name__)

_COOLDOWN_SECS = 15  # segundos entre llamadas por usuario


def init_ai():
    """Inicializa el cliente de IA con la API key de secrets"""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        logger.error("Error al configurar IA: %s", e)
        st.error("No se pudo conectar con el servicio de IA. Contacta al administrador.")
        return False


def sanitize_input(texto: str, max_len: int = 600) -> str:
    """Trunca el input a max_len caracteres para prevenir inyección de prompts."""
    if not texto:
        return ""
    return str(texto)[:max_len]


def _check_rate_limit() -> bool:
    """Verifica cooldown entre llamadas. Retorna True si se puede proceder."""
    now = time.time()
    last_call = st.session_state.get("_ai_last_call", 0)
    elapsed = now - last_call
    if elapsed < _COOLDOWN_SECS:
        remaining = int(_COOLDOWN_SECS - elapsed) + 1
        st.warning(f"Espera {remaining} segundo(s) antes de la próxima consulta.")
        return False
    st.session_state["_ai_last_call"] = now
    return True


def generate_response(prompt, max_tokens=None):
    """
    Genera una respuesta usando gemini-2.5-flash

    Args:
        prompt: El texto del prompt
        max_tokens: Tokens maximos (opcional)

    Returns:
        str: Texto de respuesta o None si hay error
    """
    if not _check_rate_limit():
        return None
    try:
        tokens = max_tokens or AI_CONFIG.get("max_tokens", 8192)
        generation_config = genai.types.GenerationConfig(max_output_tokens=tokens)
        model = genai.GenerativeModel(AI_CONFIG["model"])
        response = model.generate_content(prompt, generation_config=generation_config)
        # Extraer texto ignorando partes de "thinking" si las hay
        parts = response.candidates[0].content.parts
        texto = "".join(p.text for p in parts if not getattr(p, "thought", False))
        return texto if texto else response.text
    except Exception as e:
        logger.error("Error al generar respuesta: %s", e)
        st.error(f"[DIAG] {type(e).__name__}: {str(e)[:300]}")
        return None


def _escape_newlines_in_strings(text):
    """Escapa newlines literales dentro de valores string JSON."""
    result = []
    in_string = False
    i = 0
    while i < len(text):
        c = text[i]
        if c == '"' and (i == 0 or text[i - 1] != '\\'):
            in_string = not in_string
            result.append(c)
        elif c == '\n' and in_string:
            result.append('\\n')
        elif c == '\r' and in_string:
            result.append('\\r')
        elif c == '\t' and in_string:
            result.append('\\t')
        else:
            result.append(c)
        i += 1
    return ''.join(result)


def limpiar_json(texto):
    """Parsea JSON de respuesta IA, manejando newlines literales dentro de strings."""
    try:
        texto_limpio = texto.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(texto_limpio)
        except json.JSONDecodeError:
            return json.loads(_escape_newlines_in_strings(texto_limpio))
    except Exception:
        return None


def generate_structured_response(prompt, separador="|||"):
    """
    Genera una respuesta estructurada con separadores

    Args:
        prompt: El texto del prompt
        separador: Separador para dividir secciones

    Returns:
        list: Lista de partes separadas
    """
    response = generate_response(prompt)
    if response:
        # Limpiar asteriscos de markdown
        clean_response = response.replace("*", "")
        return clean_response.split(separador)
    return []
