"""
Feedback Constructivo - YoCreo Suite
Protocolo Estandar v2.0
"""

import streamlit as st
import json

from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import copy_button_component, create_pdf_reportlab, render_encabezado


def limpiar_json(texto):
    """Limpia la respuesta de la IA para obtener JSON valido."""
    try:
        texto_limpio = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except:
        return None


def generar_feedback_ai(nombre, rol, queja):
    """Genera feedback constructivo usando modelo SCI."""
    prompt = f"""Actua como un Coach experto en Comunicacion No Violenta y el modelo SCI (Situacion, Comportamiento, Impacto).

DATOS DEL CASO:
- Receptor: {nombre}
- Relacion: {rol}
- Queja cruda (sin filtro): "{queja}"

TU MISION:
Transformar esta queja en un feedback profesional y constructivo.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.
3. El guion debe ser directo para leer.

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "analisis": "Explica brevemente que juicios o carga emocional se detecto y elimino.",
    "hechos": "Lista los hechos objetivos detectados (lo que grabaria una camara).",
    "guion": "El guion exacto utilizando la estructura SCI (Situacion, Comportamiento, Impacto) + Pregunta final.",
    "consejo": "Un tip breve sobre el tono o momento adecuado para decirlo."
}}"""
    response = generate_response(prompt)
    if response:
        data = limpiar_json(response)
        if data:
            for key in data:
                data[key] = data[key].replace("**", "").replace("##", "")
            return data
    return None


def render():
    """Renderiza la practica Feedback Constructivo."""
    info = PRACTICAS["feedback_constructivo"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("feedback_constructivo", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Modelo SCI"):
            st.write("""
            Esta herramienta utiliza el modelo SCI para estructurar tu mensaje sin atacar a la persona:

            - Situacion: Contexto especifico (Cuando/Donde).
            - Comportamiento: Hechos observables (Que hizo, sin adjetivos).
            - Impacto: Consecuencia en ti o el equipo.
            """)

    # Estado de sesion
    if 'fb_resultado' not in st.session_state:
        st.session_state.fb_resultado = None
    if 'fb_nombre' not in st.session_state:
        st.session_state.fb_nombre = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Datos del Caso")

        col1, col2 = st.columns(2)
        with col1:
            nombre_input = st.text_input(
                "Nombre de la persona",
                placeholder="Ej: Pedro",
                key="fb_nombre_input"
            )
        with col2:
            rol_input = st.selectbox(
                "Tu relacion con ella",
                [
                    "Soy su Jefe",
                    "Somos Pares (Colegas)",
                    "Es mi Jefe",
                    "Es mi Cliente",
                    "Es mi Proveedor"
                ],
                key="fb_rol"
            )

        queja_input = st.text_area(
            "Describe la situacion (Desahogate aqui sin filtros)",
            placeholder="Ej: Estoy harto de que Pedro llegue tarde a las reuniones, es un irresponsable...",
            height=100,
            key="fb_queja_input"
        )

        if st.button("Generar Feedback", use_container_width=True):
            if nombre_input and queja_input and len(queja_input) >= 10:
                with st.spinner("Analizando hechos y filtrando emociones..."):
                    data = generar_feedback_ai(nombre_input, rol_input, queja_input)
                    if data:
                        resultado = f"""ANALISIS DE JUICIOS:
{data['analisis']}

HECHOS OBJETIVOS:
{data['hechos']}

GUION SCI:
{data['guion']}

CONSEJO:
{data['consejo']}"""
                        st.session_state.fb_resultado = resultado
                        st.session_state.fb_nombre = nombre_input
                    else:
                        st.markdown('<div class="custom-error">No se pudo generar el feedback. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Ingresa el nombre y describe la situacion (minimo 10 caracteres).</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.fb_resultado:
        with st.container(border=True):
            st.markdown("#### Resultado del Analisis")

            st.session_state.fb_resultado = st.text_area(
                "Feedback editable:",
                value=st.session_state.fb_resultado,
                height=400,
                key="edit_fb",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.fb_resultado, key="copy_fb")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value=f"Feedback_{st.session_state.fb_nombre}",
                    key="fb_fname"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="fb_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Feedback Constructivo (Modelo SCI)",
                    [("Resultado", st.session_state.fb_resultado)]
                )
                st.download_button(
                    "Descargar PDF",
                    data=pdf_data,
                    file_name=f"{fname}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.download_button(
                    "Descargar TXT",
                    data=st.session_state.fb_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
