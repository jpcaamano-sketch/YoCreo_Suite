"""
Seguimiento de Compromisos - YoCreo Suite
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


def generar_seguimiento_ai(compromiso, persona, relacion, intentos_previos, urgencia, consecuencias):
    """Genera mensajes de seguimiento en 3 tonos."""
    prompt = f"""Eres un experto en comunicacion asertiva y seguimiento de compromisos.
CONTEXTO:
- Compromiso: {compromiso}
- Responsable: {persona} ({relacion})
- Intentos previos: {intentos_previos} | Urgencia: {urgencia}
- Consecuencias: {consecuencias}

OBJETIVO: Genera 3 versiones del mensaje de seguimiento.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio, listo para copiar.

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "suave": "Texto version amable (recordatorio)...",
    "firme": "Texto version directa (reclamo)...",
    "formal": "Texto version urgente (ultimatum)..."
}}"""
    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Seguimiento de Compromisos."""
    info = PRACTICAS["seguimiento_compromisos"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("seguimiento_compromisos", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Metodologia"):
            st.write("""
            Herramienta para redactar mensajes de cobro de pendientes segun la urgencia:

            - Suave: Primer aviso o relacion delicada.
            - Firme: Insistencia necesaria.
            - Formal: Consecuencias graves o registro oficial.
            """)

    # Estado de sesion
    if 'seg_resultado' not in st.session_state:
        st.session_state.seg_resultado = None
    if 'seg_ctx' not in st.session_state:
        st.session_state.seg_ctx = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Datos del Compromiso")

        col1, col2 = st.columns(2)
        with col1:
            persona = st.text_input(
                "Persona Responsable",
                placeholder="Ej: Maria, de Finanzas",
                key="seg_persona"
            )
            relacion = st.selectbox(
                "Relacion",
                ["Jefe", "Colaborador", "Par/Colega", "Proveedor", "Cliente"],
                key="seg_relacion"
            )
        with col2:
            urgencia = st.selectbox(
                "Urgencia",
                ["Baja", "Media", "Alta", "Critica"],
                key="seg_urgencia"
            )
            intentos = st.selectbox(
                "Intentos Previos",
                ["Ninguno", "1 vez", "2-3 veces", "Multiples"],
                key="seg_intentos"
            )

        compromiso = st.text_area(
            "Compromiso Pendiente",
            placeholder="Ej: Enviar el reporte de ventas...",
            height=80,
            key="seg_compromiso"
        )
        consecuencias = st.text_input(
            "Consecuencias (Opcional)",
            placeholder="Ej: Se retrasa el cierre anual",
            key="seg_consecuencias"
        )

        if st.button("Generar Mensajes", use_container_width=True):
            if persona and compromiso:
                with st.spinner("Redactando..."):
                    data = generar_seguimiento_ai(compromiso, persona, relacion, intentos, urgencia, consecuencias)
                    if data:
                        resultado = f"""OPCION 1: SUAVE (Recordatorio)
{data['suave']}

--------------------------------------------------

OPCION 2: FIRME (Reclamo)
{data['firme']}

--------------------------------------------------

OPCION 3: FORMAL (Ultimatum)
{data['formal']}"""
                        st.session_state.seg_resultado = resultado
                        st.session_state.seg_ctx = {"compromiso": compromiso, "persona": persona}
                    else:
                        st.markdown('<div class="custom-error">No se pudieron generar los mensajes. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Indica responsable y compromiso.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.seg_resultado:
        with st.container(border=True):
            st.markdown("#### Mensajes Generados")

            st.session_state.seg_resultado = st.text_area(
                "Mensajes editables:",
                value=st.session_state.seg_resultado,
                height=400,
                key="edit_seg",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.seg_resultado, key="copy_seg")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre archivo",
                    value="Seguimiento",
                    key="seg_fname"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="seg_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Seguimiento de Compromisos",
                    [("Mensajes", st.session_state.seg_resultado)]
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
                    data=st.session_state.seg_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
