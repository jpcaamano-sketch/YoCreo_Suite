"""
Presentacion Inspiradora - YoCreo Suite
Protocolo Estandar v2.0
"""

import streamlit as st
import json

from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import copy_button_component, create_pdf_reportlab, render_encabezado
from core.analytics import registrar_uso


def limpiar_json(texto):
    """Limpia la respuesta de la IA para obtener JSON valido."""
    try:
        texto_limpio = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except:
        return None


def generar_historia_ai(dato_duro, audiencia):
    """Genera una narrativa inspiradora usando storytelling."""
    prompt = f"""Actúa como un Guionista de TED Talks experto en Storytelling.

TU MISION: Transformar un "dato aburrido" en una narrativa emocionante usando la estructura del "VIAJE DEL HEROE".

AUDIENCIA: {audiencia}
INPUT (Dato crudo): "{dato_duro}"

ESTRUCTURA OBLIGATORIA:
1. EL GANCHO: Frase inicial.
2. ACTO 1 (El Dragón): El problema.
3. ACTO 2 (La Espada): La solución.
4. ACTO 3 (El Tesoro): El futuro.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "gancho": "La frase de apertura...",
    "acto_1": "Narrativa del problema (El Dragon)...",
    "acto_2": "Narrativa de la solucion (La Espada)...",
    "acto_3": "Narrativa del futuro (El Tesoro)...",
    "metafora": "Una analogia visual breve."
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
    """Renderiza la practica Presentacion Inspiradora."""
    info = PRACTICAS["presentacion_inspiradora"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("presentacion_inspiradora", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: El Viaje del Heroe"):
            st.write("""
            Estructura narrativa claáica para presentaciones memorables:

            - El Gancho: Captura atención en 10 segundos.
            - Acto 1 (Desafío): El problema es el villano.
            - Acto 2 (Solución): Tu estrategia es la espada.
            - Acto 3 (Futuro): El tesoro que se consigue al ganar.
            """)

    # Estado de sesion
    if 'story_resultado' not in st.session_state:
        st.session_state.story_resultado = None
    if 'story_aud' not in st.session_state:
        st.session_state.story_aud = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Configuración del Relato")

        audiencia_input = st.selectbox(
            "Audiencia Objetivo",
            ["Mi Equipo", "El Directorio", "Clientes", "Toda la Empresa", "Inversionistas", "Proveedores"],
            key="presentacion_audiencia"
        )

        dato_input = st.text_area(
            "Tu dato o idea 'aburrida'",
            placeholder="Ej: Tenemos que reducir costos un 10% para mantener el margen...",
            height=100,
            key="presentacion_dato"
        )

        if st.button("Construir Narrativa", use_container_width=True):
            if dato_input and len(dato_input) >= 10:
                with st.spinner("Escribiendo el guion..."):
                    data = generar_historia_ai(dato_input, audiencia_input)
                    if data:
                        resultado = f"""GANCHO (Apertura):
{data['gancho']}

ACTO 1 (El Desafío):
{data['acto_1']}

ACTO 2 (La Estrategia):
{data['acto_2']}

ACTO 3 (El Futuro):
{data['acto_3']}

METAFORA VISUAL:
{data['metafora']}"""
                        st.session_state.story_resultado = resultado
                        st.session_state.story_aud = audiencia_input
                        registrar_uso("presentacion_inspiradora")
                    else:
                        st.markdown('<div class="custom-error">No se pudo generar el guión. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Escribe el dato o idea que quieres transformar (mínimo 10 caracteres).</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.story_resultado:
        with st.container(border=True):
            st.markdown("#### Guión de Storytelling")

            st.session_state.story_resultado = st.text_area(
                "Guion editable:",
                value=st.session_state.story_resultado,
                height=400,
                key="edit_story",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.story_resultado, key="copy_story")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value="Guion_Presentacion",
                    key="presentacion_nombre"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="presentacion_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Guion de Presentacion Inspiradora",
                    [("Guion", st.session_state.story_resultado)]
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
                    data=st.session_state.story_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
