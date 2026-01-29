"""
Core modules for YoCreo Suite
Protocolo Estandar v2.0
"""

from .config import COLORS, AI_CONFIG, APP_INFO, PRACTICAS
from .styles import apply_styles, get_css
from .ai_client import init_ai, generate_response
from .export import (
    copy_button_component,
    create_pdf_reportlab,
    create_word_document,
    get_pdf_mime,
    get_word_mime,
    show_download_section,
    render_encabezado
)
