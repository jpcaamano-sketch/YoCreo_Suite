"""
Presentacion Inspiradora - YoCreo Suite
Arquitecto de Storytelling - Transforma datos frios en historias que inspiran
"""

import streamlit as st
import json
import re
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import (
    create_word_document, create_pdf_document,
    get_word_mime, get_pdf_mime, text_area_with_copy
)


def limpiar_json(texto):
    """Limpia la respuesta de la IA para obtener JSON valido."""
    try:
        texto = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto)
    except:
        match = re.search(r'(\{.*\}|\[.*\])', texto, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
        return None


def generar_historia(dato_duro, audiencia):
    """Transforma el dato aburrido en una narrativa epica."""

    prompt = f"""Actua como un Guionista de TED Talks.

TU MISION: Transformar un "dato aburrido" en una narrativa emocionante usando la estructura del "VIAJE DEL HEROE".

INPUT (El dato crudo): "{dato_duro}"
AUDIENCIA: {audiencia}

INSTRUCCIONES DE ESTRUCTURA (3 ACTOS):
1. EL GANCHO: Una frase inicial que rompa el hielo (pregunta retorica o afirmacion shockeante).
2. ACTO 1 (El Dragon/Desafio): Pinta la situacion actual como un villano o tormenta. Que pasa si no hacemos nada?
3. ACTO 2 (La Espada/Estrategia): Presenta la solucion no como una tarea, sino como el arma para vencer al dragon.
4. ACTO 3 (El Tesoro/Futuro): Describe visualmente como sera el exito. "Imaginen..."

Responde SOLO JSON:
{{
    "gancho_apertura": "Frase corta e impactante",
    "acto_1_desafio": "Narrativa del problema",
    "acto_2_lucha": "Narrativa de la solucion",
    "acto_3_futuro": "Narrativa del beneficio final",
    "metafora_visual": "Una imagen mental o analogia para reforzar el mensaje (ej: 'Esto es como escalar el Everest...')"
}}"""

    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Presentacion Inspiradora"""
    info = PRACTICAS["presentacion_inspiradora"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    with st.expander("La estructura del Viaje del Heroe"):
        st.markdown("""
        Toda gran presentacion sigue esta estructura narrativa:

        1. **El Gancho:** Captura atencion en los primeros 10 segundos
        2. **Acto 1 - El Desafio:** Presenta el problema como un "villano" a vencer
        3. **Acto 2 - La Estrategia:** Tu solucion es el "arma heroica"
        4. **Acto 3 - El Futuro:** Visualiza el exito para inspirar accion

        *Las mejores TED Talks y pitches de negocios usan esta estructura.*
        """)

    # Inputs
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Tu dato o idea aburrida:**")
            dato_input = st.text_area(
                "Dato o idea",
                height=100,
                placeholder="Ej: Tenemos que reducir los costos operativos un 10%...",
                label_visibility="collapsed"
            )
        with col2:
            st.markdown("**Audiencia:**")
            audiencia_input = st.selectbox(
                "Audiencia",
                ["Mi Equipo", "El Directorio", "Clientes", "Toda la Empresa", "Inversionistas", "Proveedores"],
                label_visibility="collapsed"
            )

    # Estado
    if 'historia_resultado' not in st.session_state:
        st.session_state.historia_resultado = None
    if 'historia_historial' not in st.session_state:
        st.session_state.historia_historial = []

    # Boton
    if st.button("Construir Narrativa", type="primary", use_container_width=True):
        if len(dato_input) < 10:
            st.warning("Escribe un poco mas de contexto.")
        else:
            with st.spinner("Escribiendo el guion de tu presentacion..."):
                st.session_state.historia_resultado = generar_historia(dato_input, audiencia_input)
                st.session_state.historia_contexto = {
                    "dato": dato_input,
                    "audiencia": audiencia_input
                }

                # Historial
                if st.session_state.historia_resultado:
                    st.session_state.historia_historial.insert(0, {
                        "dato": dato_input[:40] + "...",
                        "audiencia": audiencia_input,
                        "resultado": st.session_state.historia_resultado
                    })
                    st.session_state.historia_historial = st.session_state.historia_historial[:5]

    # Resultados
    if st.session_state.historia_resultado:
        h = st.session_state.historia_resultado

        st.divider()

        # Tu Apertura de Impacto
        st.subheader("Tu Apertura de Impacto")

        gancho = h.get('gancho_apertura', '')
        gancho_edit = text_area_with_copy(
            "El gancho (editable):",
            gancho,
            key="gancho_edit",
            height=80
        )

        st.divider()

        # Guion completo (editable)
        st.subheader("Guion Completo")

        # Obtener contenido de los actos para el guion completo
        acto1 = h.get('acto_1_desafio', '')
        acto2 = h.get('acto_2_lucha', '')
        acto3 = h.get('acto_3_futuro', '')

        texto_completo = f"""{gancho}

{acto1}

{acto2}

{acto3}"""

        guion_completo = text_area_with_copy(
            "Copia esto para tu reunion:",
            texto_completo,
            key="guion_completo",
            height=300
        )

        st.divider()

        # Metafora visual sugerida
        st.subheader("Metafora Visual Sugerida")
        st.info(h.get('metafora_visual', ''))

        st.divider()

        # Descarga
        st.subheader("Descargar Guion")

        col_name, col_type = st.columns([2, 1])
        with col_name:
            nombre_archivo = st.text_input(
                "Nombre del archivo:",
                value="Guion_Presentacion",
                help="Sin extension"
            )
        with col_type:
            tipo_archivo = st.radio("Formato:", ["Word (.docx)", "PDF (.pdf)"], horizontal=True, key="tipo_historia")

        secciones = [
            ("Apertura de Impacto", gancho_edit),
            ("Guion Completo", guion_completo),
            ("Metafora Visual", h.get('metafora_visual', ''))
        ]

        if tipo_archivo == "Word (.docx)":
            data = create_word_document("Guion de Presentacion Inspiradora", secciones)
            mime = get_word_mime()
            ext = "docx"
        else:
            data = create_pdf_document("Guion de Presentacion Inspiradora", secciones)
            mime = get_pdf_mime()
            ext = "pdf"

        st.download_button(
            label=f"Descargar {tipo_archivo}",
            data=data,
            file_name=f"{nombre_archivo}.{ext}",
            mime=mime,
            use_container_width=True
        )

    # Historial
    st.divider()
    if st.session_state.historia_historial:
        with st.expander("Historial de guiones (ultimos 5)", expanded=False):
            for i, item in enumerate(st.session_state.historia_historial):
                st.markdown(f"**{i+1}. Para: {item['audiencia']}**")
                st.caption(f"Dato: {item['dato']}")
                if st.button(f"Cargar", key=f"cargar_historia_{i}"):
                    st.session_state.historia_resultado = item['resultado']
                    st.rerun()
                st.markdown("---")
