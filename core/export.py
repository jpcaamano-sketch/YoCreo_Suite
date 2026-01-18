"""
Funciones de exportación para YoCreo Suite
Soporta: Word (.docx), PDF (.pdf), Excel (.xlsx)
Incluye: Botón de copiar al portapapeles
"""

import io
import streamlit as st
from fpdf import FPDF
from docx import Document
import pandas as pd


# ==================== COPIAR AL PORTAPAPELES ====================

def copy_button(text, button_text="Copiar", key=None):
    """
    Muestra un botón que copia texto plano al portapapeles
    (Función legacy - usar text_area_with_copy para el nuevo estilo)
    """
    import random
    escaped_text = text.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${').replace('\n', '\\n').replace('\r', '').replace("'", "\\'")
    btn_id = f"copy_btn_{key or random.randint(1000, 9999)}"

    copy_html = f"""
    <button style="background:#F26B3A;color:white;border:none;padding:8px 16px;border-radius:5px;cursor:pointer;"
            id="{btn_id}" onclick="
                var texto = `{escaped_text}`;
                var textarea = document.createElement('textarea');
                textarea.value = texto;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                document.getElementById('{btn_id}').innerHTML='Copiado!';
                setTimeout(function(){{document.getElementById('{btn_id}').innerHTML='{button_text}';}},2000);
            ">
        {button_text}
    </button>
    """
    st.components.v1.html(copy_html, height=45)


def text_area_with_copy(label, text, key, height=120):
    """
    Muestra un text_area editable con botón de copiar pequeño

    Args:
        label: Etiqueta del campo
        text: Texto inicial
        key: Key único para el componente
        height: Altura del text_area

    Returns:
        str: El texto editado
    """
    import random

    # Text area editable
    edited_text = st.text_area(label, value=text, height=height, key=key)

    # Escapar texto para JavaScript
    escaped_text = edited_text.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${').replace('\n', '\\n').replace('\r', '').replace("'", "\\'")

    # ID único
    btn_id = f"copy_{key or random.randint(1000, 9999)}"

    # Botón pequeño estilo naranja - copia texto plano sin formato
    copy_html = f"""
    <button id="{btn_id}" onclick="
        var texto = `{escaped_text}`;
        var textarea = document.createElement('textarea');
        textarea.value = texto;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        document.getElementById('{btn_id}').innerHTML = 'Copiado!';
        document.getElementById('{btn_id}').style.background = '#28a745';
        setTimeout(function() {{
            document.getElementById('{btn_id}').innerHTML = 'Copiar';
            document.getElementById('{btn_id}').style.background = '#F26B3A';
        }}, 1500);
    " style="
        background: #F26B3A;
        color: white;
        border: none;
        padding: 4px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
    ">Copiar</button>
    """
    st.components.v1.html(copy_html, height=35)

    return edited_text


def editable_output_with_copy(label, text, key, height=120):
    """
    Alias para text_area_with_copy (compatibilidad)
    """
    return text_area_with_copy(label, text, key, height)


def clean_latin(text):
    """Limpia caracteres para compatibilidad con PDF (latin-1)"""
    if not text:
        return ""
    return text.encode('latin-1', 'replace').decode('latin-1')


# ==================== WORD ====================

def create_word_document(titulo, secciones):
    """
    Crea un documento Word con secciones

    Args:
        titulo: Título del documento
        secciones: Lista de tuplas (titulo_seccion, contenido)

    Returns:
        bytes: Contenido del archivo Word
    """
    doc = Document()
    doc.add_heading(titulo, 0)

    for seccion_titulo, contenido in secciones:
        doc.add_heading(seccion_titulo, level=1)
        doc.add_paragraph(contenido)

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


def get_word_mime():
    """Retorna el MIME type para Word"""
    return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


# ==================== PDF ====================

class YoCreoPDF(FPDF):
    """Clase PDF personalizada con header de YoCreo"""

    def __init__(self, titulo="YoCreo Suite"):
        super().__init__()
        self.titulo_doc = titulo

    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(91, 45, 144)  # Morado
        self.cell(0, 10, clean_latin(self.titulo_doc), 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'YoCreo Suite - Pagina {self.page_no()}', 0, 0, 'C')


def create_pdf_document(titulo, secciones):
    """
    Crea un documento PDF con secciones

    Args:
        titulo: Título del documento
        secciones: Lista de tuplas (titulo_seccion, contenido)

    Returns:
        bytes: Contenido del archivo PDF
    """
    pdf = YoCreoPDF(titulo)
    pdf.add_page()

    for seccion_titulo, contenido in secciones:
        # Título de sección
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(242, 107, 58)  # Naranja
        pdf.cell(0, 10, clean_latin(seccion_titulo), 0, 1)

        # Contenido
        pdf.set_text_color(51, 51, 51)  # Gris oscuro
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, clean_latin(contenido))
        pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1')


def get_pdf_mime():
    """Retorna el MIME type para PDF"""
    return "application/pdf"


# ==================== EXCEL ====================

def create_excel_document(data, sheet_name="Datos"):
    """
    Crea un documento Excel

    Args:
        data: Lista de diccionarios o DataFrame
        sheet_name: Nombre de la hoja

    Returns:
        bytes: Contenido del archivo Excel
    """
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


def get_excel_mime():
    """Retorna el MIME type para Excel"""
    return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# ==================== UTILIDADES ====================

def show_download_section(st, resultados, texto_original, nombre_default="Documento"):
    """
    Muestra la sección de descarga estándar

    Args:
        st: Módulo streamlit
        resultados: Diccionario con los resultados
        texto_original: Texto original del usuario
        nombre_default: Nombre por defecto del archivo
    """
    st.subheader("📥 Descargar Archivo")

    col_name, col_type = st.columns([2, 1])
    with col_name:
        nombre_archivo = st.text_input(
            "Nombre del archivo:",
            value=nombre_default,
            help="Sin extensión"
        )
    with col_type:
        tipo_archivo = st.radio(
            "Formato:",
            ["Word (.docx)", "PDF (.pdf)"],
            horizontal=True
        )

    # Preparar secciones
    secciones = []
    if texto_original:
        secciones.append(("Original", texto_original))
    for key, value in resultados.items():
        if value and key != "error":
            secciones.append((key.title(), value))

    # Generar archivo según tipo
    if tipo_archivo == "Word (.docx)":
        data = create_word_document("Documento YoCreo", secciones)
        mime = get_word_mime()
        ext = "docx"
    else:
        data = create_pdf_document("Documento YoCreo", secciones)
        mime = get_pdf_mime()
        ext = "pdf"

    st.download_button(
        label=f"💾 Descargar {tipo_archivo}",
        data=data,
        file_name=f"{nombre_archivo}.{ext}",
        mime=mime,
        use_container_width=True
    )
