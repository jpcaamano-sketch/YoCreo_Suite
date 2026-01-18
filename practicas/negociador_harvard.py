"""
Negociador Harvard - YoCreo Suite
Negociación basada en intereses, no posiciones
"""

import streamlit as st
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import create_word_document, create_pdf_document, get_word_mime, get_pdf_mime, text_area_with_copy


def limpiar_respuesta(texto):
    """Elimina símbolos markdown y limpia el texto"""
    import re
    texto = texto.replace("*", "").replace("#", "")
    texto = re.sub(r'\n\s*\n\s*\n', '\n\n', texto)  # Reduce saltos de línea excesivos
    return texto.strip()


def analizar_negociacion(rol, contraparte, problema, intereses_mios, intereses_ellos, maan):
    """Genera estrategia de negociación Harvard"""
    prompt = f"""
    Actúa como un Experto en Negociación del 'Harvard Negotiation Project' (Fisher & Ury).
    Tu cliente es un novato que necesita una guía paso a paso.

    CONTEXTO:
    - Usuario: {rol}
    - Contraparte: {contraparte}
    - Conflicto: {problema}
    - Intereses del Usuario (Subyacentes): {intereses_mios}
    - Intereses de la Contraparte (Estimados): {intereses_ellos}
    - MAAN (Plan B si no hay acuerdo): {maan}

    REGLAS DE FORMATO ESTRICTAS:
    - NO escribas saludos ni introducciones como "¡Excelente!", "Es un placer", "Perfecto", "Entendido"
    - NO escribas párrafos de cierre como "¡Con esta hoja de ruta...", "¡Éxito!", "Espero que...", "¡Mucho éxito!"
    - NO uses símbolos de formato markdown como ###, **, __, etc.
    - Escribe en texto plano, directo y profesional
    - Comienza DIRECTAMENTE con "1. DIAGNÓSTICO DE PODER" sin ningún texto previo

    TAREA: Genera una hoja de ruta estratégica.

    FORMATO DE RESPUESTA:

    1. DIAGNÓSTICO DE PODER
    Analiza el MAAN del usuario. ¿Es fuerte o débil? ¿Debe revelarlo o mejorarlo?

    2. ESTRATEGIA A: CREACIÓN DE VALOR (Ideal)
    Diseña una propuesta que satisfaga los intereses de ambos (Opciones de Mutuo Beneficio).
    - Propuesta creativa: [Detalle]
    - Frase de apertura ("Speech"): [Escribe el guion exacto]

    3. ESTRATEGIA B: CRITERIOS OBJETIVOS (Defensiva)
    Si la contraparte se pone dura o regatea por posición.
    - Qué estándar independiente usar (precios de mercado, leyes, precedentes).
    - Frase para re-encuadrar: "No hablemos de lo que tú quieres o yo quiero, veamos qué es lo justo basado en..."

    4. PREGUNTAS PODEROSAS
    3 preguntas que el usuario debe hacer para descubrir más información en la mesa.
    """

    response = generate_response(prompt)
    if response:
        return limpiar_respuesta(response)
    return None


def render():
    """Renderiza la práctica Negociador Harvard"""
    info = PRACTICAS["negociador_harvard"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    with st.expander("📚 ¿Qué es el Método Harvard? (Leer antes de empezar)"):
        st.info("""
        Este método no busca 'ganar' aplastando al otro, sino lograr un acuerdo sensato.
        1. **Intereses:** No te enfoques en 'posiciones' (quiero $100), sino en 'intereses' (necesito pagar la renta).
        2. **Opciones:** Busca soluciones creativas donde ambos ganen algo.
        3. **Criterios:** Usa datos objetivos (mercado, ley) para decidir, no la voluntad.
        4. **MAAN:** Tu 'As bajo la manga'. Tu plan B si no hay acuerdo.
        """)

    # Inputs
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Tu Rol:**")
            rol = st.text_input("Tu Rol", placeholder="Ej: Proveedor de Servicios", label_visibility="collapsed")
            st.markdown("**Tus Intereses (¿Para qué quieres esto?):**")
            intereses_mios = st.text_area("Tus Intereses",
                placeholder="Más allá del dinero/posición. Ej: Quiero estabilidad, prestigio, tiempo libre...", label_visibility="collapsed")

        with col2:
            st.markdown("**La Contraparte:**")
            contraparte = st.text_input("La Contraparte", placeholder="Ej: Gerente de Compras", label_visibility="collapsed")
            st.markdown("**Intereses de Ellos (¿Qué les preocupa?):**")
            intereses_ellos = st.text_area("Intereses de Ellos",
                placeholder="Ej: No pasarse del presupuesto, quedar bien con su jefe, rapidez...", label_visibility="collapsed")

        st.markdown("**El Conflicto/Tema a negociar:**")
        problema = st.text_area("Conflicto",
            placeholder="Ej: Renovación de contrato con aumento de tarifas del 20%.", label_visibility="collapsed")

        st.markdown("**Tu Poder (MAAN):**")
        st.caption("MAAN = Mejor Alternativa al Acuerdo Negociado. Es tu Plan B real.")
        maan = st.text_input("MAAN",
            placeholder="Ej: Tengo otra oferta lista de la empresa X / Me quedo sin cliente.", label_visibility="collapsed")

    # Estado
    if 'harvard_resultado' not in st.session_state:
        st.session_state.harvard_resultado = None

    # Botón
    if st.button("🧠 Generar Estrategias", type="primary", use_container_width=True):
        if not intereses_mios or not maan:
            st.warning("⚠️ Para Harvard, es crucial definir tus Intereses y tu MAAN.")
        else:
            with st.spinner("Analizando intereses y opciones de mutuo beneficio..."):
                st.session_state.harvard_resultado = analizar_negociacion(
                    rol, contraparte, problema, intereses_mios, intereses_ellos, maan
                )

    # Resultados
    if st.session_state.harvard_resultado:
        res = st.session_state.harvard_resultado

        st.divider()
        st.subheader("Hoja de Ruta")
        st.caption("Puedes editar los textos antes de copiar o descargar")

        resultado_edit = text_area_with_copy(
            "Estrategia de negociación:",
            res,
            key="harvard_edit",
            height=400
        )

        st.divider()

        # Descarga
        st.subheader("Descargar Plan")
        c_name, c_type = st.columns([2, 1])
        with c_name:
            f_name = st.text_input("Nombre del archivo:", value="Estrategia_Harvard")
        with c_type:
            f_fmt = st.radio("Formato:", ["Word (.docx)", "PDF (.pdf)"], horizontal=True)

        secciones = [("Estrategia de Negociación", resultado_edit)]

        if f_fmt == "Word (.docx)":
            data = create_word_document("Plan de Negociación Harvard", secciones)
            mime = get_word_mime()
            ext = "docx"
        else:
            data = create_pdf_document("Plan de Negociación Harvard", secciones)
            mime = get_pdf_mime()
            ext = "pdf"

        st.download_button(
            label=f"💾 Descargar {f_fmt}",
            data=data,
            file_name=f"{f_name}.{ext}",
            mime=mime,
            use_container_width=True
        )
