"""
Escucha Activa - YoCreo Suite
Protocolo Estandar v2.0
"""

import streamlit as st
import json
import re

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
        match = re.search(r'(\{.*\}|\[.*\])', texto, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
        return None


def generar_personaje():
    """Crea un personaje frustrado aleatorio con alta variabilidad."""
    prompt = """Genera un caso de roleplay para practicar escucha activa.

IDIOMA: Espanol latinoamericano (sin vosotros, usa tu/usted).

Inventa un contexto original (laboral, familiar, pareja, salud, economico, etc).
El personaje debe estar estresado, triste o preocupado.
Escribe un monologo de 3-5 frases natural y emocional.

Responde SOLO con este JSON (sin texto adicional):
{"nombre": "Nombre", "rol": "Rol", "emocion_dominante": "Emocion", "texto_monologo": "El monologo aqui..."}"""
    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def evaluar_respuesta(caso_original, respuesta_usuario):
    """Evalua si el usuario escucho o si dio consejos."""
    prompt = f"""Actua como Supervisor de Coaching. Evalua la respuesta del usuario ante una queja.

CASO ORIGINAL (Dijo el personaje): "{caso_original}"
RESPUESTA DEL USUARIO (Dijo el coach): "{respuesta_usuario}"

CRITERIOS DE EVALUACION:
1. PROHIBIDO ACONSEJAR: Si el usuario dice "deberias", "tienes que", "por que no pruebas", "yo en tu lugar", califica con 0 en empatia.
2. VALIDACION: El usuario reconocio la emocion explicita o implicita?
3. PARAFRASEO: El usuario resumio los hechos principales sin agregar de su cosecha?

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "consejo_detectado": true/false,
    "puntaje": (Numero del 1 al 10),
    "feedback_positivo": "Lo que hizo bien...",
    "feedback_mejora": "Lo que le falto...",
    "ejemplo_ideal": "Respuesta perfecta de Reflective Listening"
}}"""
    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Escucha Activa."""
    info = PRACTICAS["escucha_activa"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("escucha_activa", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Regla de Oro"):
            st.write("""
            NO des consejos ni soluciones.
            Solo escucha, valida la emocion y resume lo que entendiste.

            Evita frases como:
            - "Deberias..."
            - "Por que no pruebas..."
            - "Yo en tu lugar..."
            """)

    # Estado de sesion
    if 'escucha_caso' not in st.session_state:
        st.session_state.escucha_caso = None
    if 'escucha_evaluacion' not in st.session_state:
        st.session_state.escucha_evaluacion = None
    if 'escucha_historial' not in st.session_state:
        st.session_state.escucha_historial = []

    # ==================== CAJA 2: SIMULADOR ====================
    with st.container(border=True):
        st.markdown("#### Simulador de Escucha")

        if st.button("Traer nuevo interlocutor", use_container_width=True):
            with st.spinner("Buscando a alguien que necesita ser escuchado..."):
                resultado = generar_personaje()
                if resultado:
                    st.session_state.escucha_caso = resultado
                    st.session_state.escucha_evaluacion = None
                    st.rerun()
                else:
                    st.markdown('<div class="custom-error">No se pudo generar el personaje. Intenta de nuevo.</div>', unsafe_allow_html=True)

        if st.session_state.escucha_caso:
            caso = st.session_state.escucha_caso
            st.markdown(f"**{caso.get('nombre', 'Persona')} ({caso.get('rol', 'Desconocido')}) te dice:**")

            monologo = caso.get('texto_monologo', '')
            st.text_area(
                "Monologo:",
                value=f'"{monologo}"',
                height=100,
                disabled=True,
                label_visibility="collapsed"
            )

            st.write("Tu mision: Demuestrale que le entendiste. NO soluciones su problema.")

            respuesta_user = st.text_area(
                "Tu respuesta (Escribe lo que le dirias):",
                placeholder="Escribe aqui tu respuesta de escucha activa...",
                height=100,
                key="respuesta_escucha"
            )

            if st.button("Evaluar mi Escucha", use_container_width=True):
                if len(respuesta_user) < 5:
                    st.markdown('<div class="custom-warning">Escribe una respuesta mas completa antes de evaluar.</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Analizando tu empatia..."):
                        evaluacion = evaluar_respuesta(monologo, respuesta_user)
                        st.session_state.escucha_evaluacion = evaluacion

                        if evaluacion:
                            st.session_state.escucha_historial.insert(0, {
                                "personaje": caso.get('nombre', 'Persona'),
                                "monologo": monologo[:50] + "...",
                                "puntaje": evaluacion.get('puntaje', 0)
                            })
                            st.session_state.escucha_historial = st.session_state.escucha_historial[:5]
                            registrar_uso("escucha_activa")
        else:
            st.write("Presiona el boton para comenzar el simulacro.")

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.escucha_evaluacion:
        ev = st.session_state.escucha_evaluacion

        with st.container(border=True):
            st.markdown("#### Veredicto del Coach")

            score = ev.get('puntaje', 0)

            if ev.get('consejo_detectado'):
                st.markdown('<div class="custom-error">ALERTA: Intentaste dar un consejo. En la escucha activa pura, primero debemos validar.</div>', unsafe_allow_html=True)

            resultado_texto = f"""PUNTAJE: {score}/10

LO BUENO:
{ev.get('feedback_positivo', '')}

A MEJORAR:
{ev.get('feedback_mejora', '')}

RESPUESTA IDEAL:
{ev.get('ejemplo_ideal', '')}"""

            st.session_state.escucha_resultado_texto = st.text_area(
                "Evaluacion editable:",
                value=resultado_texto,
                height=300,
                key="edit_escucha",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.escucha_resultado_texto, key="copy_escucha")

    # ==================== HISTORIAL ====================
    if st.session_state.escucha_historial:
        with st.expander("Historial de practicas (ultimas 5)"):
            for i, item in enumerate(st.session_state.escucha_historial):
                st.write(f"{i+1}. {item['personaje']} - Puntaje: {item['puntaje']}/10")
                st.caption(f"Caso: {item['monologo']}")
