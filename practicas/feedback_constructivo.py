"""
Feedback Constructivo - YoCreo Suite
Transforma quejas en feedback profesional usando el modelo SCI
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
        texto_limpio = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except:
        match = re.search(r'(\{.*\}|\[.*\])', texto, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
        return None


def limpiar_guion(texto):
    """Elimina símbolos markdown y corchetes del texto"""
    if not texto:
        return texto
    texto = texto.replace("*", "").replace("#", "")
    texto = texto.replace("[", "").replace("]", "")
    return texto.strip()


def analizar_feedback(nombre, rol, queja):
    """Transforma la queja en un guion de feedback profesional usando SCI."""

    prompt = f"""Actua como un Coach experto en Comunicacion No Violenta y Liderazgo.
Tu tarea es transformar una "queja emocional" en un guion de feedback profesional usando el modelo SCI (Situacion, Comportamiento, Impacto).

DATOS DEL CASO:
- Receptor: {nombre}
- Relacion: {rol}
- Queja cruda (sin filtro): "{queja}"

INSTRUCCIONES:
1. Analiza el nivel de agresividad/juicio del texto original (1 a 10).
2. Identifica los HECHOS (lo que una camara podria grabar) y separalos de los JUICIOS (opiniones).
3. Redacta un guion que el usuario pueda leer textualmente.

RESPONDE SOLO CON ESTE FORMATO JSON:
{{
    "nivel_toxicidad": 8,
    "analisis_juicios": "Texto breve explicando que juicios se eliminaron (ej: se quito 'es un flojo').",
    "hechos_detectados": "Lista breve de los hechos objetivos.",
    "guion_sci": "El guion exacto, amable y firme, listo para leer. Debe incluir Situacion, Comportamiento, Impacto y una pregunta final.",
    "consejo_extra": "Un tip breve sobre lenguaje corporal o tono."
}}"""

    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Feedback Constructivo"""
    info = PRACTICAS["feedback_constructivo"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    with st.expander("Que es el modelo SCI?"):
        st.markdown("""
        El modelo **SCI** (Situacion - Comportamiento - Impacto) es una tecnica para dar feedback sin atacar a la persona:

        - **Situacion:** Describe cuando y donde ocurrio (contexto)
        - **Comportamiento:** Que hizo la persona (hechos observables)
        - **Impacto:** Como te afecto a ti o al equipo

        *Al eliminar adjetivos como "irresponsable" o "flojo", reducimos la defensividad y abrimos el dialogo.*
        """)

    # Inputs
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Nombre de la persona:**")
            nombre_input = st.text_input("Nombre de la persona", placeholder="Ej: Pedro", label_visibility="collapsed")
        with col2:
            st.markdown("**Tu relación con ella:**")
            rol_input = st.selectbox("Tu relacion con ella", [
                "Soy su Jefe",
                "Somos Pares (Colegas)",
                "Es mi Jefe",
                "Es mi Cliente",
                "Es mi Proveedor",
                "Otro"
            ], label_visibility="collapsed")

        st.markdown("**Describe la situación (Desahógate aquí sin filtros):**")
        queja_input = st.text_area(
            "Describe la situacion",
            height=120,
            placeholder="Ej: Estoy harto de que Pedro llegue tarde a las reuniones, es un irresponsable y me hace quedar mal con los clientes...",
            label_visibility="collapsed"
        )

    # Estado
    if 'feedback_resultado' not in st.session_state:
        st.session_state.feedback_resultado = None
    if 'feedback_historial' not in st.session_state:
        st.session_state.feedback_historial = []

    # Boton de accion
    if st.button("Transformar en Feedback Profesional", type="primary", use_container_width=True):
        if not queja_input or len(queja_input) < 10:
            st.warning("Por favor escribe un poco mas de detalle sobre la situacion.")
        else:
            with st.spinner("Analizando hechos, filtrando emociones y redactando guion..."):
                st.session_state.feedback_resultado = analizar_feedback(nombre_input, rol_input, queja_input)
                st.session_state.feedback_contexto = {
                    "nombre": nombre_input,
                    "rol": rol_input,
                    "queja": queja_input
                }

                # Historial
                if st.session_state.feedback_resultado:
                    st.session_state.feedback_historial.insert(0, {
                        "nombre": nombre_input or "Sin nombre",
                        "queja": queja_input[:40] + "...",
                        "resultado": st.session_state.feedback_resultado
                    })
                    st.session_state.feedback_historial = st.session_state.feedback_historial[:5]

    # Mostrar resultados
    if st.session_state.feedback_resultado:
        datos = st.session_state.feedback_resultado

        st.divider()

        # Termometro de toxicidad
        nivel = datos.get("nivel_toxicidad", 5)

        st.subheader("Diagnostico de tu entrada")

        col_bar, col_msg = st.columns([3, 1])
        with col_bar:
            st.progress(nivel / 10)
        with col_msg:
            if nivel <= 4:
                st.success(f"**{nivel}/10**")
                mensaje = "Tu mensaje era bastante neutral."
            elif nivel <= 7:
                st.warning(f"**{nivel}/10**")
                mensaje = "Tu mensaje tenia carga emocional."
            else:
                st.error(f"**{nivel}/10**")
                mensaje = "Tu mensaje era muy agresivo/toxico."

        st.caption(f"Nivel de carga emocional detectado: {mensaje}")

        # Analisis
        with st.expander("Ver que se elimino (Analisis del Coach)"):
            st.write(f"**Hechos rescatados:** {datos.get('hechos_detectados', '')}")
            st.write(f"**Juicios eliminados:** {datos.get('analisis_juicios', '')}")

        st.divider()

        # Guion SCI (editable con icono copiar)
        st.subheader("Guion Sugerido (SCI)")

        guion = limpiar_guion(datos.get("guion_sci", ""))

        guion_editado = text_area_with_copy(
            "Edita y copia el guion:",
            guion,
            key="guion_sci_edit",
            height=180
        )

        # Consejo extra
        st.success(f"**Tip Extra:** {datos.get('consejo_extra', '')}")

        st.divider()

        # Descarga
        st.subheader("Descargar Documento")

        col_name, col_type = st.columns([2, 1])
        with col_name:
            ctx = st.session_state.get('feedback_contexto', {})
            nombre_archivo = st.text_input(
                "Nombre del archivo:",
                value=f"Feedback_{ctx.get('nombre', 'Persona').split()[0] if ctx.get('nombre') else 'Documento'}",
                help="Sin extension"
            )
        with col_type:
            tipo_archivo = st.radio("Formato:", ["Word (.docx)", "PDF (.pdf)"], horizontal=True, key="tipo_feedback")

        secciones = [
            ("Situacion Original", ctx.get('queja', '')),
            ("Analisis", f"Hechos: {datos.get('hechos_detectados', '')}\nJuicios eliminados: {datos.get('analisis_juicios', '')}"),
            ("Guion SCI", guion_editado),
            ("Consejo", datos.get('consejo_extra', ''))
        ]

        if tipo_archivo == "Word (.docx)":
            data = create_word_document("Feedback Constructivo SCI", secciones)
            mime = get_word_mime()
            ext = "docx"
        else:
            data = create_pdf_document("Feedback Constructivo SCI", secciones)
            mime = get_pdf_mime()
            ext = "pdf"

        st.download_button(
            label=f"Descargar {tipo_archivo}",
            data=data,
            file_name=f"{nombre_archivo}.{ext}",
            mime=mime,
            use_container_width=True
        )

    # Pie educativo
    st.divider()
    st.caption("**Por que funciona?** El modelo SCI separa lo que VEMOS (Hechos) de lo que SENTIMOS (Impacto). Al eliminar adjetivos como 'irresponsable' o 'flojo', reducimos la defensividad del otro y abrimos el dialogo.")

    # Historial
    if st.session_state.feedback_historial:
        with st.expander("Historial de conversiones (ultimas 5)", expanded=False):
            for i, item in enumerate(st.session_state.feedback_historial):
                st.markdown(f"**{i+1}. {item['nombre']}:** {item['queja']}")
                if st.button(f"Cargar", key=f"cargar_feedback_{i}"):
                    st.session_state.feedback_resultado = item['resultado']
                    st.rerun()
                st.markdown("---")
