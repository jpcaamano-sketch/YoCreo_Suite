"""
Cliente de IA para YoCreo Suite
Actualmente usa Google Gemini, preparado para migrar a Claude
"""

import streamlit as st
import google.generativeai as genai
from .config import AI_CONFIG


def init_ai():
    """Inicializa el cliente de IA con la API key de secrets"""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"⚠️ Error al configurar IA: {e}")
        st.info("Asegúrate de tener GOOGLE_API_KEY en .streamlit/secrets.toml")
        return False


def generate_response(prompt, max_tokens=None):
    """
    Genera una respuesta usando el modelo de IA configurado

    Args:
        prompt: El texto del prompt
        max_tokens: Tokens máximos (opcional, usa config si no se especifica)

    Returns:
        str: Texto de respuesta o None si hay error
    """
    try:
        tokens = max_tokens or AI_CONFIG.get("max_tokens", 4096)
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=tokens
        )
        model = genai.GenerativeModel(AI_CONFIG["model"])
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        st.error(f"Error al generar respuesta: {e}")
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
