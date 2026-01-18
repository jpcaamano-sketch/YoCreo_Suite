"""
Planificador de Reuniones - YoCreo Suite
Diseña agendas efectivas con IA
"""

import streamlit as st
import json
import re
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import (
    create_word_document, create_pdf_document, create_excel_document,
    get_word_mime, get_pdf_mime, get_excel_mime, copy_button
)


def generar_planificacion(tema, objetivo, duracion):
    """Genera planificación de reunión en formato JSON"""
    prompt = f"""
    Actúa como un Facilitador Experto. Diseña una agenda para una reunión de {duracion} minutos.
    TEMA: {tema} | OBJETIVO: {objetivo}

    Responde EXCLUSIVAMENTE con un JSON válido.
    NO utilices bloques de código markdown (```json). Entrega solo el JSON crudo.

    Estructura obligatoria:
    {{
        "agenda": [
            {{"minutos": "00-05", "actividad": "...", "responsable": "..."}},
            {{"minutos": "...", "actividad": "...", "responsable": "..."}}
        ],
        "consejos": "Consejo 1... Consejo 2..."
    }}
    """
    return generate_response(prompt)


def procesar_respuesta(texto_completo):
    """Extrae JSON válido de la respuesta"""
    try:
        texto_limpio = texto_completo.replace("```json", "").replace("```", "").strip()

        try:
            datos = json.loads(texto_limpio)
            return datos["agenda"], datos["consejos"]
        except json.JSONDecodeError:
            match = re.search(r'(\{.*\}|\[.*\])', texto_completo, re.DOTALL)
            if match:
                json_str = match.group(0)
                datos = json.loads(json_str)
                return datos["agenda"], datos["consejos"]
            else:
                return None, "No se encontró un JSON válido en la respuesta."

    except Exception as e:
        return None, f"Error al procesar datos: {str(e)}"


def render():
    """Renderiza la práctica Planificador de Reuniones"""
    info = PRACTICAS["planificador_reuniones"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    # Inputs
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Tema:**")
            tema_input = st.text_input("Tema:", placeholder="Ej: Planificación Q1", label_visibility="collapsed")
            st.markdown("**Objetivo:**")
            obj_input = st.text_input("Objetivo:", placeholder="Ej: Aprobar presupuesto", label_visibility="collapsed")
        with col2:
            st.markdown("**Duración:**")
            duracion_input = st.selectbox("Minutos:", [15, 30, 45, 60], index=1, label_visibility="collapsed")

    # Estado
    if 'reunion_agenda' not in st.session_state:
        st.session_state.reunion_agenda = None
        st.session_state.reunion_consejos = None

    # Botón
    if st.button("⚡ Generar Planificación", type="primary", use_container_width=True):
        if not tema_input or not obj_input:
            st.warning("⚠️ Completa los campos.")
        else:
            with st.spinner("Creando estrategia..."):
                texto_raw = generar_planificacion(tema_input, obj_input, duracion_input)
                agenda_data, consejos_data = procesar_respuesta(texto_raw)

                if agenda_data:
                    st.session_state.reunion_agenda = agenda_data
                    st.session_state.reunion_consejos = consejos_data
                    st.session_state.reunion_tema = tema_input
                    st.session_state.reunion_objetivo = obj_input
                else:
                    st.error(consejos_data)

    # Resultados
    if st.session_state.reunion_agenda:
        st.subheader("Tu Agenda")

        # Mostrar tabla
        st.table(st.session_state.reunion_agenda)

        # Preparar texto para copiar
        agenda_copy = "\n".join([
            f"{item['minutos']}: {item['actividad']} ({item['responsable']})"
            for item in st.session_state.reunion_agenda
        ])

        col_info, col_copy = st.columns([5, 1])
        with col_info:
            st.info(f"**Tips:** {st.session_state.reunion_consejos}")
        with col_copy:
            copy_button(agenda_copy, "Copiar", key="copy_agenda")

        st.divider()

        # Descarga
        st.subheader("📥 Descargar Archivo")

        c_nombre, c_tipo = st.columns([2, 1])
        with c_nombre:
            nombre_archivo = st.text_input("Nombre del archivo:", value="Agenda_Reunion")
        with c_tipo:
            tipo_archivo = st.radio("Formato:", ["Word", "PDF", "Excel"], horizontal=True)

        tema = st.session_state.get('reunion_tema', tema_input)
        objetivo = st.session_state.get('reunion_objetivo', obj_input)
        agenda = st.session_state.reunion_agenda
        consejos = st.session_state.reunion_consejos

        if tipo_archivo == "Word":
            agenda_text = "\n".join([f"- {item['minutos']}: {item['actividad']} ({item['responsable']})" for item in agenda])
            secciones = [
                ("Tema", tema),
                ("Objetivo", objetivo),
                ("Agenda", agenda_text),
                ("Consejos", consejos)
            ]
            data = create_word_document("Plan de Reunión", secciones)
            mime = get_word_mime()
            ext = "docx"
        elif tipo_archivo == "PDF":
            agenda_text = "\n".join([f"- {item['minutos']}: {item['actividad']} ({item['responsable']})" for item in agenda])
            secciones = [
                ("Tema", tema),
                ("Objetivo", objetivo),
                ("Agenda", agenda_text),
                ("Consejos", consejos)
            ]
            data = create_pdf_document("Plan de Reunión", secciones)
            mime = get_pdf_mime()
            ext = "pdf"
        else:  # Excel
            data = create_excel_document(agenda, "Agenda")
            mime = get_excel_mime()
            ext = "xlsx"

        st.download_button(
            label=f"💾 Descargar en {tipo_archivo}",
            data=data,
            file_name=f"{nombre_archivo}.{ext}",
            mime=mime,
            use_container_width=True
        )
