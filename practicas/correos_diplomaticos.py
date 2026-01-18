"""
Correo Diplomático - YoCreo Suite
Convierte borradores difíciles en comunicación efectiva
"""

import streamlit as st
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import create_word_document, create_pdf_document, get_word_mime, get_pdf_mime, text_area_with_copy


def generar_opciones(texto, destinatario, tono):
    """Genera 3 versiones del mensaje con IA"""
    separador = "|||"

    tonos_desc = {
        "Neutro": "equilibrado y objetivo",
        "Cordial": "amable y cálido",
        "Urgente": "con sentido de prioridad y acción inmediata",
        "Empático": "comprensivo y considerado con los sentimientos del otro"
    }
    tono_descripcion = tonos_desc.get(tono, "equilibrado")

    prompt = f"""Eres un experto en comunicación asertiva y redacción profesional.

MENSAJE ORIGINAL A TRANSFORMAR:
\"\"\"
{texto}
\"\"\"

CONTEXTO:
- Destinatario: {destinatario}
- Tono requerido: {tono} ({tono_descripcion})

TU TAREA:
Reescribe el mensaje completo transformándolo en comunicación asertiva y diplomática.
- MANTÉN todos los puntos y argumentos del mensaje original
- ELIMINA el tono agresivo, sarcasmo, ataques personales y lenguaje pasivo-agresivo
- CONSERVA la esencia y los pedidos/solicitudes del mensaje
- El resultado debe ser un correo COMPLETO, listo para enviar, con saludo y despedida

IMPORTANTE: Cada versión debe ser un correo COMPLETO de longitud similar al original, NO un resumen.

REGLAS DE FORMATO ESTRICTAS:
- NO escribas introducciones como "Aquí tienes...", "A continuación...", "Estas son..."
- NO escribas explicaciones ni comentarios
- SOLO escribe los correos directamente
- Comienza DIRECTAMENTE con "Versión Profesional:" sin ningún texto previo

Genera exactamente 3 versiones. Usa el separador "{separador}" entre cada una:

Versión Profesional:
[Correo completo en tono formal y corporativo]
{separador}
Versión Directa:
[Correo completo en tono ejecutivo y al grano, pero respetuoso]
{separador}
Versión Coloquial:
[Correo completo en tono cercano y amigable, pero profesional]"""

    response = generate_response(prompt)

    if response:
        partes = response.replace("*", "").split(separador)
        return {
            "profesional": partes[0].replace("Versión Profesional:", "").strip() if len(partes) > 0 else "Error",
            "directo": partes[1].replace("Versión Directa:", "").strip() if len(partes) > 1 else "Error",
            "coloquial": partes[2].replace("Versión Coloquial:", "").strip() if len(partes) > 2 else "Error"
        }
    return {"error": "No se pudo generar respuesta"}


def render():
    """Renderiza la práctica Correo Diplomático"""
    info = PRACTICAS["correos_diplomaticos"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    # Inputs
    with st.container(border=True):
        st.markdown("**¿A quién le escribes?**")
        destinatario = st.selectbox(
            "Destinatario",
            ["Cliente", "Jefe/Superior", "Colaborador/Equipo", "Proveedor",
             "Par (Colega/Igual)", "Recursos Humanos", "Cliente Interno", "Comité/Directorio"],
            label_visibility="collapsed"
        )

        st.markdown("**¿Qué tono prefieres?**")
        tono = st.selectbox(
            "Tono",
            ["Neutro", "Cordial", "Urgente", "Empático"],
            help="Neutro: equilibrado | Cordial: amable | Urgente: con prioridad | Empático: comprensivo",
            label_visibility="collapsed"
        )

        st.markdown("**Borrador del texto (sin filtro):**")
        texto_input = st.text_area(
            "Borrador",
            height=120,
            placeholder="Ej: Necesito que me entregues eso ahora mismo o tendremos problemas...",
            label_visibility="collapsed"
        )

    # Estado de sesión
    if 'correos_resultado' not in st.session_state:
        st.session_state.correos_resultado = None
    if 'correos_historial' not in st.session_state:
        st.session_state.correos_historial = []

    # Botón de acción
    if st.button("✨ Generar Propuestas", type="primary", use_container_width=True):
        if not texto_input:
            st.warning("Escribe un borrador primero.")
        else:
            with st.spinner("Analizando tono y reescribiendo..."):
                st.session_state.correos_resultado = generar_opciones(texto_input, destinatario, tono)
                st.session_state.correos_texto_original = texto_input

                # Guardar en historial
                st.session_state.correos_historial.insert(0, {
                    "original": texto_input,
                    "destinatario": destinatario,
                    "tono": tono,
                    "resultado": st.session_state.correos_resultado
                })
                st.session_state.correos_historial = st.session_state.correos_historial[:5]

    # Resultados
    if st.session_state.correos_resultado:
        res = st.session_state.correos_resultado

        if "error" in res:
            st.error(f"Error técnico: {res['error']}")
        else:
            st.markdown("### Opciones Asertivas")
            st.caption("Puedes editar los textos antes de copiar o descargar")

            version_profesional = text_area_with_copy(
                "Profesional (Formal):",
                res.get('profesional', ''),
                key="edit_profesional",
                height=150
            )

            version_directa = text_area_with_copy(
                "Directo (Ejecutivo):",
                res.get('directo', ''),
                key="edit_directo",
                height=150
            )

            version_coloquial = text_area_with_copy(
                "Coloquial (Cercano):",
                res.get('coloquial', ''),
                key="edit_coloquial",
                height=150
            )

            res_editado = {
                "profesional": version_profesional,
                "directo": version_directa,
                "coloquial": version_coloquial
            }

            st.divider()

            # Zona de descarga
            st.subheader("📥 Descargar Archivo")

            col_name, col_type = st.columns([2, 1])
            with col_name:
                nombre_archivo = st.text_input("Nombre del archivo:", value="Mis_Propuestas", help="Sin extensión")
            with col_type:
                tipo_archivo = st.radio("Formato:", ["Word (.docx)", "PDF (.pdf)"], horizontal=True)

            texto_orig = st.session_state.get('correos_texto_original', texto_input)

            secciones = [
                ("Original", texto_orig),
                ("1. Profesional", res_editado['profesional']),
                ("2. Directo", res_editado['directo']),
                ("3. Coloquial", res_editado['coloquial'])
            ]

            if tipo_archivo == "Word (.docx)":
                data = create_word_document("Propuestas de Comunicación", secciones)
                mime = get_word_mime()
                ext = "docx"
            else:
                data = create_pdf_document("Propuestas de Comunicación", secciones)
                mime = get_pdf_mime()
                ext = "pdf"

            st.download_button(
                label=f"💾 Descargar {tipo_archivo}",
                data=data,
                file_name=f"{nombre_archivo}.{ext}",
                mime=mime,
                use_container_width=True
            )

    # Historial
    st.divider()
    if st.session_state.correos_historial:
        with st.expander("📜 Historial de conversiones (últimas 5)", expanded=False):
            for i, item in enumerate(st.session_state.correos_historial):
                st.markdown(f"**{i+1}. Para: {item['destinatario']} | Tono: {item['tono']}**")
                orig = item['original']
                st.caption(f"Original: {orig[:100]}..." if len(orig) > 100 else f"Original: {orig}")
                if st.button(f"Cargar esta conversión", key=f"cargar_correos_{i}"):
                    st.session_state.correos_resultado = item['resultado']
                    st.session_state.correos_texto_original = item['original']
                    st.rerun()
                st.markdown("---")
