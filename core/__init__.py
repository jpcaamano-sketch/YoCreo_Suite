"""
Core modules for YoCreo Suite
"""

from .config import COLORS, AI_CONFIG, APP_INFO, PRACTICAS
from .styles import apply_styles, show_logo, show_header, get_css
from .ai_client import init_ai, generate_response, generate_structured_response
from .export import (
    create_word_document, create_pdf_document, create_excel_document,
    get_word_mime, get_pdf_mime, get_excel_mime,
    show_download_section
)
