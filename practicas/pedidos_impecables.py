"""
Pedidos Impecables - YoCreo Suite
Protocolo Estandar v2.0
"""

import streamlit as st
import json
from datetime import date

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


def generar_pedido_ai(oyente, accion, condiciones, tiempo, trasfondo):
    """Genera una carta formal con un pedido impecable."""
    prompt = f"""Actua como un experto en comunicacion corporativa y ontologia del lenguaje.
Redacta una CARTA FORMAL que constituya un PEDIDO IMPECABLE.

DATOS DEL PEDIDO:
1. DESTINATARIO: {oyente}
2. ACCION REQUERIDA: {accion}
3. CONDICIONES DE SATISFACCION: {condiciones}
4. FECHA LIMITE: {tiempo}
5. CONTEXTO/TRASFONDO: {trasfondo}

INSTRUCCIONES:
- El texto debe ser solo el cuerpo de la carta/mensaje.
- Debe ser directo, amable pero firme, y muy claro.
- Justo antes de la despedida, incluye una frase que busque el COMPROMISO del receptor.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "carta": "Texto completo de la carta..."
}}"""
    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Pedidos Impecables."""
    info = PRACTICAS["pedidos_impecables"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("pedidos_impecables", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Los 5 Actos Lingüísticos"):
            st.write("""
            Un pedido impecable incluye 5 elementos:

            1. OYENTE: A quién va dirigido
            2. ACCION: Qué se solicita específicamente
            3. CONDICIONES: Cómo debe cumplirse
            4. TIEMPO: Cuándo debe estar listo
            5. TRASFONDO: Para qué se necesita
            """)

    # Estado de sesion
    if 'pedido_resultado' not in st.session_state:
        st.session_state.pedido_resultado = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Datos del Pedido")

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            oyente_in = st.text_input(
                "Oyente (Destinatario)",
                placeholder="Ej: Juan, Jefe de Marketing",
                key="pedidos_oyente"
            )
        with col2:
            fecha_in = st.date_input(
                "Fecha Límite",
                min_value=date.today(),
                key="pedidos_fecha"
            )
        with col3:
            hora_in = st.time_input(
                "Hora Límite",
                key="pedidos_hora"
            )

        tiempo_str = f"{fecha_in.strftime('%d/%m/%Y')} a las {hora_in.strftime('%H:%M')}"

        accion_in = st.text_area(
            "Acción (Qué necesitas)",
            placeholder="Ej: Enviar el reporte de ventas",
            height=70,
            key="pedidos_accion"
        )

        condiciones_in = st.text_area(
            "Condiciones de Satisfacción (Cómo)",
            placeholder="Ej: En formato Excel, con gráficos comparativos",
            height=70,
            key="pedidos_condiciones"
        )

        trasfondo_in = st.text_area(
            "Trasfondo (Para qué)",
            placeholder="Ej: Para presentar en la reunión de directorio",
            height=70,
            key="pedidos_trasfondo"
        )

        if st.button("Generar Pedido", use_container_width=True):
            if oyente_in and accion_in:
                with st.spinner("Redactando carta..."):
                    data = generar_pedido_ai(oyente_in, accion_in, condiciones_in, tiempo_str, trasfondo_in)
                    if data and 'carta' in data:
                        st.session_state.pedido_resultado = data['carta']
                        registrar_uso("pedidos_impecables")
                    else:
                        st.markdown('<div class="custom-error">No se pudo generar el pedido. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">El Oyente y la Accion son obligatorios.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.pedido_resultado:
        with st.container(border=True):
            st.markdown("#### Carta Generada")

            st.session_state.pedido_resultado = st.text_area(
                "Carta editable:",
                value=st.session_state.pedido_resultado,
                height=350,
                key="edit_pedido",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.pedido_resultado, key="copy_pedido")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value="Solicitud_Formal",
                    key="pedidos_nombre"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="pedidos_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Solicitud Formal",
                    [("Carta", st.session_state.pedido_resultado)]
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
                    data=st.session_state.pedido_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
