"""
Correos Diplomaticos - YoCreo Suite
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


def generar_correos_ai(texto, destinatario, tono):
    """Genera 3 versiones de un mensaje diplomático."""
    prompt = f"""Eres un experto en comunicación asertiva y redacción profesional.

MENSAJE ORIGINAL: "{texto}"
DESTINATARIO: {destinatario}
TONO DESEADO: {tono}

TU TAREA:
Genera 3 versiones del correo (Profesional, Directa, Coloquial) transformando el mensaje original en comunicacion asertiva.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.
3. El resultado debe ser un correo completo (Asunto, Cuerpo, Despedida).

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "profesional": "Texto completo version formal...",
    "directa": "Texto completo version ejecutiva...",
    "coloquial": "Texto completo version cercana..."
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
    """Renderiza la practica Correos Diplomaticos."""
    info = PRACTICAS["correos_diplomaticos"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("correos_diplomaticos", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Como funciona"):
            st.write("""
            Esta herramienta reescribe tus borradores eliminando la agresividad o la pasividad, y te propone 3 posibles respuestas:

            - Profesional: Formal y estructurado
            - Directo: Ejecutivo y al punto
            - Coloquial: Cercano y amigable
            """)

    # Estado de sesion
    if 'mail_resultado' not in st.session_state:
        st.session_state.mail_resultado = None
    if 'mail_versions' not in st.session_state:
        st.session_state.mail_versions = None
    if 'mail_original' not in st.session_state:
        st.session_state.mail_original = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Tu Borrador")

        col1, col2 = st.columns(2)
        with col1:
            destinatario = st.selectbox(
                "Destinatario",
                ["Cliente", "Jefe/Superior",  "Par (Colega)", "Colaborador/Equipo", "Proveedor","RRHH", "Comité"],
                key="correos_destinatario"
            )
        with col2:
            tono = st.selectbox(
                "Tono Principal",
                ["Neutro", "Cordial", "Urgente", "Empático"],
                key="correos_tono"
            )

        texto_input = st.text_area(
            "Borrador del texto (sin filtro)",
            placeholder="Ej: Necesito que me entregues eso ahora mismo o tendremos problemas...",
            height=100,
            key="correos_texto"
        )

        if st.button("Generar Propuestas", use_container_width=True):
            if texto_input:
                with st.spinner("Reescribiendo mensajes..."):
                    data = generar_correos_ai(texto_input, destinatario, tono)
                    if data:
                        st.session_state.mail_versions = data
                        st.session_state.mail_original = texto_input
                        resultado = f"""ORIGINAL:
{texto_input}

--- VERSION PROFESIONAL ---
{data['profesional']}

--- VERSION DIRECTA ---
{data['directa']}

--- VERSION COLOQUIAL ---
{data['coloquial']}"""
                        st.session_state.mail_resultado = resultado
                    else:
                        st.markdown('<div class="custom-error">No se pudieron generar las propuestas. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Por favor escribe un borrador primero.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.mail_resultado:
        with st.container(border=True):
            st.markdown("#### Propuestas Generadas")

            st.session_state.mail_resultado = st.text_area(
                "Propuestas editables:",
                value=st.session_state.mail_resultado,
                height=400,
                key="edit_mail",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.mail_resultado, key="copy_mail")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value="Propuestas_Mensaje",
                    key="correos_nombre"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="correos_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Propuestas de Comunicacion",
                    [("Resultado", st.session_state.mail_resultado)]
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
                    data=st.session_state.mail_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
