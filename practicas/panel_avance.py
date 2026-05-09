"""
Panel de Avance del Usuario — YoCreo Suite
3 capas: Mapa de prácticas, Tus zonas, Tu estilo emergente.
"""

import logging
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict
import streamlit as st
from core.database import get_supabase

logger = logging.getLogger(__name__)

# ── Mapeo dimensiones ────────────────────────────────────────────────────────

DIMENSIONES = {
    "Planificación y Foco": {
        "icon": "🎯",
        "practicas": ["priorizador_tareas", "seguimiento_compromisos", "definicion_objetivos", "planificador_reuniones"],
    },
    "Comunicación e Influencia": {
        "icon": "💬",
        "practicas": ["presentacion_inspiradora", "pedidos_impecables", "correos_diplomaticos", "negociador_harvard"],
    },
    "Vínculo y Empatía": {
        "icon": "🤝",
        "practicas": ["escucha_activa", "preguntas_desafiantes", "disculpas_efectivas"],
    },
    "Desarrollo de Personas": {
        "icon": "🌱",
        "practicas": ["delegacion_situacional", "feedback_constructivo", "evaluacion_desempeno"],
    },
}

PRACTICAS_NOMBRES = {
    "priorizador_tareas":       "Priorizador",
    "planificador_reuniones":   "Reuniones",
    "pedidos_impecables":       "Pedidos",
    "delegacion_situacional":   "Delegación",
    "correos_diplomaticos":     "Mensajes",
    "seguimiento_compromisos":  "Compromisos",
    "escucha_activa":           "Escucha Activa",
    "feedback_constructivo":    "Feedback",
    "evaluacion_desempeno":     "Evaluación",
    "negociador_harvard":       "Negociador",
    "presentacion_inspiradora": "Presentación",
    "preguntas_desafiantes":    "Preguntas",
    "definicion_objetivos":     "Objetivos",
    "disculpas_efectivas":      "Disculpas",
}

TODAS_LAS_PRACTICAS = list(PRACTICAS_NOMBRES.keys())


# ── Carga de datos ────────────────────────────────────────────────────────────

def _cargar_eventos(email: str) -> list:
    """Carga todos los eventos de practice_events para el usuario."""
    try:
        supabase = get_supabase()
        resp = (
            supabase.table("practice_events")
            .select("practice_key, created_at")
            .eq("email", email.lower())
            .order("created_at", desc=False)
            .execute()
        )
        return resp.data if resp.data else []
    except Exception as e:
        logger.warning("Error cargando eventos: %s", e)
        return []


def _calcular_racha(eventos: list) -> int:
    """Calcula la racha de días consecutivos con al menos un uso."""
    if not eventos:
        return 0
    fechas = set()
    for e in eventos:
        try:
            dt = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
            fechas.add(dt.date())
        except Exception:
            pass
    if not fechas:
        return 0
    hoy = datetime.now(timezone.utc).date()
    ayer = hoy - timedelta(days=1)
    inicio = hoy if hoy in fechas else (ayer if ayer in fechas else None)
    if not inicio:
        return 0
    racha = 0
    dia = inicio
    while dia in fechas:
        racha += 1
        dia -= timedelta(days=1)
    return racha


# ── Capa 1: Mapa de prácticas ─────────────────────────────────────────────────

def _capa_mapa(conteo: Counter, total_sesiones: int):
    exploradas   = sum(1 for k in TODAS_LAS_PRACTICAS if conteo[k] > 0)
    sin_explorar = len(TODAS_LAS_PRACTICAS) - exploradas
    racha        = st.session_state.get("_panel_racha", 0)

    # Métricas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sesiones totales",   total_sesiones)
    c2.metric("Prácticas exploradas", exploradas)
    c3.metric("Sin explorar",        sin_explorar)
    c4.metric("Racha (días)",        racha)

    st.markdown("---")

    # Leyenda
    st.markdown(
        """<div style="display:flex;gap:20px;margin-bottom:12px;font-size:13px;">
            <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#BBBBBB;margin-right:5px;"></span>Sin usar</span>
            <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#F5C518;margin-right:5px;"></span>1–2 usos</span>
            <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#27AE60;margin-right:5px;"></span>3+ usos</span>
        </div>""",
        unsafe_allow_html=True
    )

    # Grid de tarjetas (4 columnas)
    cols = st.columns(4)
    for i, key in enumerate(TODAS_LAS_PRACTICAS):
        usos = conteo[key]
        if usos == 0:
            color = "#BBBBBB"
        elif usos <= 2:
            color = "#F5C518"
        else:
            color = "#27AE60"

        nombre = PRACTICAS_NOMBRES[key]
        with cols[i % 4]:
            st.markdown(
                f"""<div style="border:1px solid #e0e0e0;border-radius:10px;padding:12px 8px;
                                text-align:center;margin-bottom:8px;background:#fafafa;">
                    <div style="width:14px;height:14px;border-radius:50%;background:{color};
                                margin:0 auto 8px auto;"></div>
                    <div style="font-size:12px;font-weight:600;color:#333;line-height:1.3;">{nombre}</div>
                    <div style="font-size:11px;color:#888;margin-top:4px;">{usos} uso{"s" if usos != 1 else ""}</div>
                </div>""",
                unsafe_allow_html=True
            )


# ── Capa 2: Tus zonas ─────────────────────────────────────────────────────────

def _etiqueta_zona(pct: float) -> tuple[str, str]:
    """Retorna (etiqueta, color) según el porcentaje."""
    if pct >= 90:
        return "Zona de confort", "#3498DB"
    elif pct >= 40:
        return "En crecimiento", "#27AE60"
    else:
        return "Zona ciega", "#E74C3C"


def _capa_zonas(conteo: Counter):
    MAX_USOS_POR_PRACTICA = 5  # usos que equivalen al 100% de una práctica

    for nombre_dim, datos in DIMENSIONES.items():
        practicas = datos["practicas"]
        icon      = datos["icon"]

        usos_dim  = sum(min(conteo[p], MAX_USOS_POR_PRACTICA) for p in practicas)
        maximo    = len(practicas) * MAX_USOS_POR_PRACTICA
        pct       = round((usos_dim / maximo) * 100) if maximo > 0 else 0

        etiqueta, color_etq = _etiqueta_zona(pct)

        with st.container(border=True):
            col_txt, col_etq = st.columns([3, 1])
            with col_txt:
                st.markdown(f"**{icon} {nombre_dim}**")
            with col_etq:
                st.markdown(
                    f"""<div style="text-align:right;">
                        <span style="background:{color_etq};color:white;
                                     font-size:11px;padding:3px 10px;border-radius:12px;
                                     font-weight:600;">{etiqueta}</span>
                    </div>""",
                    unsafe_allow_html=True
                )

            st.progress(pct / 100)

            # Mini-fila de prácticas de la dimensión
            subcols = st.columns(len(practicas))
            for j, p in enumerate(practicas):
                usos = conteo[p]
                dot  = "🟢" if usos >= 3 else ("🟡" if usos >= 1 else "⚪")
                with subcols[j]:
                    st.markdown(
                        f"<div style='font-size:11px;text-align:center;color:#555;'>"
                        f"{dot}<br>{PRACTICAS_NOMBRES[p]}</div>",
                        unsafe_allow_html=True
                    )

        st.markdown("")


# ── Capa 3: Tu estilo emergente ───────────────────────────────────────────────

def _capa_estilo(conteo: Counter, total_sesiones: int):
    MINIMO_SESIONES = 10

    if total_sesiones < MINIMO_SESIONES:
        faltantes = MINIMO_SESIONES - total_sesiones
        st.info(
            f"Esta sección se activa después de **{MINIMO_SESIONES} sesiones**. "
            f"Te faltan **{faltantes}** para desbloquearla."
        )
        st.progress(total_sesiones / MINIMO_SESIONES)
        return

    # Verificar si ya hay perfil generado en session_state
    cache_key = "_perfil_liderazgo"
    if cache_key in st.session_state:
        _mostrar_perfil(st.session_state[cache_key])
        return

    if st.button("Generar mi perfil de liderazgo", type="primary", use_container_width=True):
        with st.spinner("Analizando tus patrones de uso con IA..."):
            perfil = _generar_perfil_ia(conteo, total_sesiones)
        if perfil:
            st.session_state[cache_key] = perfil
            _mostrar_perfil(perfil)
        else:
            st.error("No se pudo generar el perfil. Intenta de nuevo.")


def _generar_perfil_ia(conteo: Counter, total_sesiones: int) -> dict | None:
    """Genera el perfil con Gemini. Retorna dict con texto y tags o None si falla."""
    try:
        import google.generativeai as genai
        from core.config import AI_CONFIG

        # Construir resumen de uso
        practicas_ordenadas = sorted(
            [(PRACTICAS_NOMBRES[k], conteo[k]) for k in TODAS_LAS_PRACTICAS if conteo[k] > 0],
            key=lambda x: -x[1]
        )
        resumen_uso = "\n".join([f"- {nombre}: {usos} uso(s)" for nombre, usos in practicas_ordenadas])

        # Calcular dimensiones más usadas
        dims_uso = {}
        for nombre_dim, datos in DIMENSIONES.items():
            dims_uso[nombre_dim] = sum(conteo[p] for p in datos["practicas"])
        dim_top = max(dims_uso, key=dims_uso.get)
        dim_baja = min(dims_uso, key=dims_uso.get)

        prompt = f"""Eres un coach de liderazgo experto. Analiza los patrones de uso de un líder
en una suite de prácticas de liderazgo y genera un perfil breve y motivador.

DATOS DEL LÍDER:
- Total de sesiones: {total_sesiones}
- Dimensión más desarrollada: {dim_top}
- Dimensión menos explorada: {dim_baja}
- Prácticas utilizadas (de más a menos):
{resumen_uso}

Genera exactamente este formato separado por |||:

[Un párrafo de 3-4 oraciones describiendo el estilo de liderazgo emergente del usuario,
en segunda persona (tú), basado en sus patrones de uso. Sé específico, inspirador y honesto.]
|||
[3 fortalezas en formato: Etiqueta corta (3-4 palabras)]
|||
[2 áreas de desarrollo en formato: Etiqueta corta (3-4 palabras)]

No uses asteriscos ni markdown. Solo texto plano."""

        model = genai.GenerativeModel(AI_CONFIG["model"])
        resp  = model.generate_content(prompt)
        partes = resp.text.split("|||")
        if len(partes) < 3:
            return None

        fortalezas = [t.strip().lstrip("-•").strip() for t in partes[1].strip().split("\n") if t.strip()]
        areas      = [t.strip().lstrip("-•").strip() for t in partes[2].strip().split("\n") if t.strip()]

        return {
            "texto":      partes[0].strip(),
            "fortalezas": fortalezas[:3],
            "areas":      areas[:2],
        }
    except Exception as e:
        logger.error("Error generando perfil IA: %s", e)
        return None


def _mostrar_perfil(perfil: dict):
    st.markdown(
        f"""<div style="background:#f4f1ff;border-radius:12px;padding:20px 24px;
                        border-left:4px solid #4E32AD;margin-bottom:16px;">
            <p style="color:#333;font-size:15px;line-height:1.7;margin:0;">{perfil['texto']}</p>
        </div>""",
        unsafe_allow_html=True
    )

    col_f, col_a = st.columns(2)
    with col_f:
        st.markdown("**Fortalezas**")
        for f in perfil.get("fortalezas", []):
            st.markdown(
                f'<span style="display:inline-block;background:#E8F8F0;color:#1E8449;'
                f'padding:4px 12px;border-radius:12px;font-size:13px;margin:3px 2px;">{f}</span>',
                unsafe_allow_html=True
            )
    with col_a:
        st.markdown("**Áreas de desarrollo**")
        for a in perfil.get("areas", []):
            st.markdown(
                f'<span style="display:inline-block;background:#FEF9E7;color:#B7770D;'
                f'padding:4px 12px;border-radius:12px;font-size:13px;margin:3px 2px;">{a}</span>',
                unsafe_allow_html=True
            )

    if st.button("Regenerar perfil", type="secondary"):
        del st.session_state["_perfil_liderazgo"]
        st.rerun()


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    st.markdown("## Mi Avance")

    user  = st.session_state.get("user", {})
    email = user.get("email", "")
    if not email:
        st.error("No se pudo obtener el usuario.")
        return

    # Cargar eventos una sola vez por sesión (o al forzar refresh)
    cache_eventos = "_panel_eventos"
    if cache_eventos not in st.session_state:
        with st.spinner("Cargando tu historial..."):
            eventos = _cargar_eventos(email)
            st.session_state[cache_eventos]  = eventos
            st.session_state["_panel_racha"] = _calcular_racha(eventos)

    eventos = st.session_state[cache_eventos]
    conteo  = Counter(e["practice_key"] for e in eventos)
    total   = len(eventos)

    # Botón de actualizar
    if st.button("Actualizar datos", type="secondary"):
        for k in [cache_eventos, "_panel_racha", "_perfil_liderazgo"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown("")

    tab1, tab2, tab3 = st.tabs(["🗺️ Mapa de prácticas", "📊 Tus zonas", "✨ Tu estilo emergente"])

    with tab1:
        _capa_mapa(conteo, total)

    with tab2:
        _capa_zonas(conteo)

    with tab3:
        _capa_estilo(conteo, total)
