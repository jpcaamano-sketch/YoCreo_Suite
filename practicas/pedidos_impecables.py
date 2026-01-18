"""
Pedidos Impecables - YoCreo Suite
Basado en la Ontología del Lenguaje (Fernando Flores)
"""

import streamlit as st
from datetime import date
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import create_word_document, create_pdf_document, get_word_mime, get_pdf_mime, text_area_with_copy


def limpiar_texto(texto):
    """Elimina símbolos markdown del texto"""
    return texto.replace("*", "").replace("#", "").strip()


def formatear_fecha_es(fecha, hora):
    """Formatea fecha y hora en español"""
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    dia_nombre = dias[fecha.weekday()]
    mes_nombre = meses[fecha.month - 1]
    return f"{dia_nombre} {fecha.day} de {mes_nombre} antes de las {hora.strftime('%H:%M')}"


def generar_pedido_ia(oyente, accion, condiciones, tiempo, contexto):
    """Genera un pedido impecable con IA"""
    prompt = f"""
    Actúa como un Coach Ontológico experto en Fernando Flores.
    Redacta un "PEDIDO IMPECABLE" basado en:

    1. OYENTE: {oyente}
    2. ACCIÓN: {accion}
    3. CONDICIONES DE SATISFACCIÓN: {condiciones}
    4. TIEMPO: {tiempo}
    5. TRASFONDO: {contexto}

    Genera dos partes separadas claramente por la etiqueta "SECCION_ANALISIS":

    Parte 1: El GUION (listo para copiar/pegar, tono profesional y asertivo).
    Parte 2: SECCION_ANALISIS: Una explicación breve de por qué este pedido reduce incertidumbre.
    """

    response = generate_response(prompt)

    if response:
        text = response
        if "SECCION_ANALISIS" in text:
            parts = text.split("SECCION_ANALISIS")
            guion = parts[0].replace("SECCION_ANALISIS", "").replace("Parte 1:", "").strip()
            analisis = parts[1].replace("Parte 2:", "").strip()
        else:
            guion = text
            analisis = "No se generó el análisis detallado."

        return limpiar_texto(guion), limpiar_texto(analisis)
    return "Error al generar", ""


def render():
    """Renderiza la práctica Pedidos Impecables"""
    info = PRACTICAS["pedidos_impecables"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])
    st.write("Completa los 5 componentes de un pedido efectivo para evitar malentendidos.")

    # Inputs
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("**¿A quién le pides?**")
            oyente = st.text_input("Oyente", placeholder="Ej: Juan, Jefe de Marketing", label_visibility="collapsed")
        with col2:
            st.markdown("**Fecha límite:**")
            fecha = st.date_input("Fecha límite", min_value=date.today(), label_visibility="collapsed")
        with col3:
            st.markdown("**Hora límite:**")
            hora = st.time_input("Hora límite", label_visibility="collapsed")

        # Formatear tiempo para el prompt
        tiempo = formatear_fecha_es(fecha, hora)

        st.markdown("**Acción (¿Qué necesitas?):**")
        accion = st.text_area("Acción",
            placeholder="Ej: Que envíes el reporte de ventas", height=100, label_visibility="collapsed")
        st.markdown("**Condiciones de Satisfacción (Estándar):**")
        condiciones = st.text_area("Condiciones",
            placeholder="Ej: Formato PDF, incluyendo gráficos de Q1", height=100, label_visibility="collapsed")
        st.markdown("**Trasfondo (¿Para qué?):**")
        contexto = st.text_area("Trasfondo",
            placeholder="Ej: Para la reunión de directorio del lunes", height=100, label_visibility="collapsed")

    # Estado
    if 'pedido_resultado' not in st.session_state:
        st.session_state.pedido_resultado = None

    # Botón
    if st.button("🚀 GENERAR PEDIDO", type="primary", use_container_width=True):
        if not oyente or not accion or not tiempo:
            st.warning("⚠️ Faltan datos clave: Oyente, Acción y Tiempo son obligatorios.")
        else:
            with st.spinner("Construyendo acto del habla con IA..."):
                guion_gen, analisis_gen = generar_pedido_ia(oyente, accion, condiciones, tiempo, contexto)

                if "Error al generar" in guion_gen:
                    st.error(guion_gen)
                else:
                    st.session_state.pedido_resultado = {
                        "guion": guion_gen,
                        "analisis": analisis_gen,
                        "oyente": oyente
                    }
                    st.rerun()

    # Resultados
    if st.session_state.pedido_resultado:
        res = st.session_state.pedido_resultado

        st.divider()
        st.subheader("Tu Pedido Listo")
        st.caption("Puedes editar los textos antes de copiar o descargar")

        guion_edit = text_area_with_copy(
            "Guion sugerido:",
            res['guion'],
            key="pedido_guion_edit",
            height=200
        )

        with st.expander("Ver Análisis (Por qué funciona)"):
            st.write(res['analisis'])

        st.divider()

        # Descarga
        st.subheader("Descargar Pedido")
        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.download_button(
                label="Descargar Texto (.txt)",
                data=guion_edit,
                file_name=f"pedido_{res['oyente']}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col_d2:
            secciones = [
                ("Guion Sugerido", guion_edit),
                ("Análisis Ontológico", res['analisis'])
            ]
            data = create_word_document("PEDIDO IMPECABLE", secciones)

            st.download_button(
                label="Descargar Word (.docx)",
                data=data,
                file_name=f"pedido_{res['oyente']}.docx",
                mime=get_word_mime(),
                use_container_width=True
            )

        # Botón reiniciar
        if st.button("🔄 Hacer Nuevo Pedido", use_container_width=True):
            st.session_state.pedido_resultado = None
            st.rerun()
