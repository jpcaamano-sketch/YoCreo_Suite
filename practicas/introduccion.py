"""
Introduccion - YoCreo Suite (rediseño v2)
Página de inicio personalizada con datos reales del usuario.
"""

import streamlit as st
import streamlit.components.v1 as components
from collections import Counter
from datetime import datetime, timezone, timedelta
from core.config import PRACTICAS


# ── Dimensiones para esta página ─────────────────────────────────────────────

DIMENSIONES_INTRO = {
    "Autogestión y Foco": {
        "num": "01", "icon": "🛡️", "bg": "#EEEDFE",
        "practicas": ["priorizador_tareas", "presentacion_inspiradora"],
    },
    "Coordinación Impecable": {
        "num": "02", "icon": "⚡", "bg": "#FAEEDA",
        "practicas": ["pedidos_impecables", "delegacion_situacional",
                      "correos_diplomaticos", "seguimiento_compromisos"],
    },
    "Desarrollo de Otros": {
        "num": "03", "icon": "🌱", "bg": "#E1F5EE",
        "practicas": ["escucha_activa", "preguntas_desafiantes",
                      "feedback_constructivo", "evaluacion_desempeno"],
    },
    "Estrategia y Relaciones": {
        "num": "04", "icon": "🎯", "bg": "#FAECE7",
        "practicas": ["definicion_objetivos", "planificador_reuniones",
                      "negociador_harvard", "disculpas_efectivas"],
    },
}

PRACTICAS_CORTOS = {
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

TODAS_LAS_PRACTICAS = list(PRACTICAS_CORTOS.keys())


# ── Carga de datos ────────────────────────────────────────────────────────────

def _cargar_datos(email: str) -> dict:
    """Carga eventos desde Supabase o reutiliza cache de session_state."""
    from core.database import get_supabase

    cache_key = "_panel_eventos"
    if cache_key not in st.session_state:
        try:
            supabase = get_supabase()
            resp = (
                supabase.table("practice_events")
                .select("practice_key, created_at")
                .eq("email", email.lower())
                .order("created_at", desc=False)
                .execute()
            )
            eventos = resp.data if resp.data else []
        except Exception:
            eventos = []
        st.session_state[cache_key] = eventos
        st.session_state["_panel_racha"] = _calcular_racha(eventos)

    eventos = st.session_state[cache_key]
    racha   = st.session_state.get("_panel_racha", 0)
    conteo  = Counter(e["practice_key"] for e in eventos)
    total   = len(eventos)
    activas = sum(1 for k in TODAS_LAS_PRACTICAS if conteo[k] > 0)

    # Zona ciega: dimensión con menor % de prácticas usadas
    zona_ciega = None
    if total > 0:
        pct_dims = {}
        for nombre, datos in DIMENSIONES_INTRO.items():
            usadas = sum(1 for p in datos["practicas"] if conteo[p] > 0)
            pct_dims[nombre] = usadas / len(datos["practicas"])
        zona_ciega = min(pct_dims, key=pct_dims.get)

    # Eventos recientes para accesos rápidos
    eventos_desc = sorted(eventos, key=lambda e: e["created_at"], reverse=True)

    return {
        "total":   total,
        "activas": activas,
        "racha":   racha,
        "conteo":  conteo,
        "zona_ciega":   zona_ciega,
        "eventos_desc": eventos_desc,
    }


def _calcular_racha(eventos: list) -> int:
    if not eventos:
        return 0
    fechas = set()
    for e in eventos:
        try:
            dt = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
            fechas.add(dt.date())
        except Exception:
            pass
    hoy  = datetime.now(timezone.utc).date()
    ayer = hoy - timedelta(days=1)
    inicio = hoy if hoy in fechas else (ayer if ayer in fechas else None)
    if not inicio:
        return 0
    racha, dia = 0, inicio
    while dia in fechas:
        racha += 1
        dia -= timedelta(days=1)
    return racha


def _hace_n_dias(iso_str: str) -> str:
    try:
        dt   = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        diff = datetime.now(timezone.utc) - dt
        d    = diff.days
        if d == 0:   return "hoy"
        if d == 1:   return "ayer"
        if d < 30:   return f"hace {d} días"
        if d < 365:  return f"hace {d // 30} mes(es)"
        return f"hace {d // 365} año(s)"
    except Exception:
        return ""


# ── Tour de onboarding ────────────────────────────────────────────────────────

def _mostrar_onboarding_tour():
    """Muestra un tour de bienvenida la primera vez (rastreado en localStorage)."""
    components.html("""
<script>
(function() {
    var doc = window.parent.document;
    if (window.parent.localStorage.getItem('yocreo_onboarding_v1') === '1') return;
    if (doc.getElementById('yc-onboarding')) return;

    var STEPS = [
        {icon:'👋', title:'Bienvenido a YoCreo Suite',
         desc:'Tu plataforma de herramientas para el liderazgo consciente. Te mostramos cómo sacarle el máximo provecho en 3 pasos.'},
        {icon:'📋', title:'Elige una práctica',
         desc:'En el menú lateral encontrarás 14 prácticas organizadas en 4 categorías: Autogestión, Coordinación, Desarrollo de Otros y Estrategia.'},
        {icon:'✍️', title:'Ingresa tu situación',
         desc:'Describe brevemente tu caso real. La IA analizará el contexto y generará un plan de acción personalizado en segundos.'},
        {icon:'📥', title:'Descarga y guarda el resultado',
         desc:'Edita la propuesta, cópiala al portapapeles o descárgala en PDF. Tu historial guarda las últimas generaciones automáticamente.'}
    ];
    var current = 0;

    function destroy() {
        window.parent.localStorage.setItem('yocreo_onboarding_v1', '1');
        var el = doc.getElementById('yc-onboarding');
        if (el) el.parentNode.removeChild(el);
    }

    var overlay = doc.createElement('div');
    overlay.id = 'yc-onboarding';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(15,8,40,0.78);display:flex;align-items:center;justify-content:center;z-index:999999;font-family:Inter,Arial,sans-serif;';

    var card = doc.createElement('div');
    card.style.cssText = 'background:#fff;border-radius:20px;padding:40px 36px;max-width:480px;width:90%;box-shadow:0 24px 64px rgba(0,0,0,0.4);text-align:center;';

    var iconEl  = doc.createElement('div');
    iconEl.style.cssText  = 'font-size:52px;margin-bottom:14px;';
    var titleEl = doc.createElement('div');
    titleEl.style.cssText = 'font-size:21px;font-weight:700;color:#1a1a2e;margin-bottom:10px;';
    var descEl  = doc.createElement('div');
    descEl.style.cssText  = 'font-size:14px;color:#555;line-height:1.65;margin-bottom:28px;';

    var dotsEl = doc.createElement('div');
    dotsEl.style.cssText = 'display:flex;gap:8px;justify-content:center;margin-bottom:28px;';
    var dots = [];
    STEPS.forEach(function(_, i) {
        var d = doc.createElement('div');
        d.style.cssText = 'width:10px;height:10px;border-radius:50%;background:' + (i===0?'#4E32AD':'#ddd') + ';transition:background 0.3s;';
        dotsEl.appendChild(d); dots.push(d);
    });

    var nextBtn = doc.createElement('button');
    nextBtn.style.cssText = 'background:#FF6B4E;color:#fff;border:none;border-radius:10px;padding:14px 32px;font-size:15px;font-weight:600;cursor:pointer;width:100%;font-family:Inter,Arial,sans-serif;';
    var skipBtn = doc.createElement('button');
    skipBtn.innerText = 'Saltar tour';
    skipBtn.style.cssText = 'background:transparent;color:#bbb;border:none;font-size:12px;cursor:pointer;margin-top:12px;display:block;width:100%;font-family:Inter,Arial,sans-serif;';

    function update() {
        var s = STEPS[current];
        iconEl.innerText  = s.icon;
        titleEl.innerText = s.title;
        descEl.innerText  = s.desc;
        dots.forEach(function(d, i) { d.style.background = i===current ? '#4E32AD' : '#ddd'; });
        nextBtn.innerText = current < STEPS.length-1 ? 'Siguiente →' : 'Comenzar';
    }

    nextBtn.addEventListener('click', function() {
        if (current < STEPS.length-1) { current++; update(); } else { destroy(); }
    });
    skipBtn.addEventListener('click', destroy);

    card.appendChild(iconEl); card.appendChild(titleEl); card.appendChild(descEl);
    card.appendChild(dotsEl); card.appendChild(nextBtn); card.appendChild(skipBtn);
    overlay.appendChild(card);
    doc.body.appendChild(overlay);
    update();
})();
</script>
""", height=0)


# ── Bloque 1: Hero personalizado ──────────────────────────────────────────────

def _bloque_hero(nombre: str, datos: dict):
    total   = datos["total"]
    activas = datos["activas"]
    racha   = datos["racha"]
    zona_ciega = datos.get("zona_ciega")

    # Nombre: hasta 2 palabras
    partes = nombre.strip().split() if nombre else ["Líder"]
    nombre_display = " ".join(partes[:2]).title()

    if total == 0:
        subtitulo = "Comienza hoy tu camino de liderazgo consciente. Todas las prácticas te esperan."
    elif racha >= 2:
        sufijo = f"Tu zona ciega está en <strong>{zona_ciega}</strong> — es donde más puedes crecer hoy." if zona_ciega else ""
        subtitulo = f"Llevas <strong>{racha} días</strong> consecutivos practicando. {sufijo}"
    elif racha == 1:
        sufijo = f"Tu zona ciega está en <strong>{zona_ciega}</strong> — es donde más puedes crecer hoy." if zona_ciega else ""
        subtitulo = f"Hoy volviste a practicar. {sufijo}"
    else:
        sufijo = f"Tu zona ciega está en <strong>{zona_ciega}</strong> — es donde más puedes crecer hoy." if zona_ciega else ""
        subtitulo = f"Es un buen momento para retomar el ritmo. {sufijo}"

    # Hero — solo HTML visual, sin botones ocultos
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#3C3489 0%,#534AB7 100%);
            border-radius:16px 16px 0 0;padding:36px 32px 28px 32px;color:white;
            position:relative;overflow:hidden;">
    <div style="position:absolute;width:220px;height:220px;border-radius:50%;
                background:rgba(255,255,255,0.05);top:-60px;right:-60px;pointer-events:none;"></div>
    <div style="position:absolute;width:140px;height:140px;border-radius:50%;
                background:rgba(255,255,255,0.05);bottom:-40px;right:80px;pointer-events:none;"></div>
    <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                opacity:0.65;margin-bottom:10px;">Bienvenido de vuelta</div>
    <div style="font-size:30px;font-weight:800;margin-bottom:12px;line-height:1.2;">Hola, {nombre_display}</div>
    <div style="font-size:14px;opacity:0.85;line-height:1.65;margin-bottom:28px;">{subtitulo}</div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.18);margin:0 0 20px 0;">
    <div style="display:flex;">
        <div style="flex:1;">
            <div style="font-size:28px;font-weight:800;">{total}</div>
            <div style="font-size:11px;opacity:0.65;margin-top:3px;">Sesiones</div>
        </div>
        <div style="width:1px;background:rgba(255,255,255,0.18);margin:0 24px;"></div>
        <div style="flex:1;">
            <div style="font-size:28px;font-weight:800;">{activas}</div>
            <div style="font-size:11px;opacity:0.65;margin-top:3px;">Prácticas activas</div>
        </div>
        <div style="width:1px;background:rgba(255,255,255,0.18);margin:0 24px;"></div>
        <div style="flex:1;">
            <div style="font-size:28px;font-weight:800;">{racha}</div>
            <div style="font-size:11px;opacity:0.65;margin-top:3px;">Días de racha</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Botón pegado visualmente al hero (borde superior recto, misma paleta)
    st.markdown("""
<style>
div[data-testid="stButton"]:has(button[data-testid="baseButton-primary"]) {
    margin-top: 0 !important;
}
div[data-testid="stButton"]:has(button[data-testid="baseButton-primary"]) button {
    border-radius: 0 0 16px 16px !important;
    background: #534AB7 !important;
    border-color: #534AB7 !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 14px !important;
}
div[data-testid="stButton"]:has(button[data-testid="baseButton-primary"]) button:hover {
    background: #4A3DA8 !important;
    border-color: #4A3DA8 !important;
}
</style>
""", unsafe_allow_html=True)

    if st.button("Ver mi avance →", key="btn_hero_avance", type="primary", use_container_width=True):
        st.session_state.practica_sel = "panel_avance"
        st.rerun()


# ── Bloque 2: Ecosistema dual ─────────────────────────────────────────────────

def _bloque_ecosistema():
    st.markdown("""
<div style="background:white;border:1px solid #E8E6F0;border-radius:14px;
            padding:24px 28px;margin-top:16px;">
    <div style="font-size:18px;font-weight:700;color:#3C3489;margin-bottom:10px;">
        Un ecosistema dual
    </div>
    <div style="font-size:14px;color:#888780;line-height:1.7;margin-bottom:20px;">
        La Suite YoCreo es a la vez un set práctico de herramientas y un camino de evolución
        personal. Un viaje que va desde el dominio interior, pasa por la excelencia con otros
        y llega a la maestría estratégica.
    </div>
    <div style="display:flex;gap:12px;">
        <div style="flex:1;background:#F5F4FA;border-radius:10px;padding:14px 16px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#534AB7;flex-shrink:0;"></div>
                <div style="font-size:13px;font-weight:700;color:#26215C;">Dominio interior</div>
            </div>
            <div style="font-size:11px;color:#888780;padding-left:18px;">Autogestión y foco</div>
        </div>
        <div style="flex:1;background:#F5F4FA;border-radius:10px;padding:14px 16px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#27AE60;flex-shrink:0;"></div>
                <div style="font-size:13px;font-weight:700;color:#26215C;">Excelencia con otros</div>
            </div>
            <div style="font-size:11px;color:#888780;padding-left:18px;">Coordinación y desarrollo</div>
        </div>
        <div style="flex:1;background:#F5F4FA;border-radius:10px;padding:14px 16px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#FF6B4E;flex-shrink:0;"></div>
                <div style="font-size:13px;font-weight:700;color:#26215C;">Maestría estratégica</div>
            </div>
            <div style="font-size:11px;color:#888780;padding-left:18px;">Visión y relaciones</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Bloque 3: El camino del líder consciente ──────────────────────────────────

def _badge_dimension(pct: float) -> str:
    if pct >= 90:
        return '<span style="background:#E8F8F0;color:#1E8449;font-size:10px;font-weight:700;padding:2px 8px;border-radius:8px;">Zona de confort</span>'
    elif pct >= 40:
        return '<span style="background:#EBF5FB;color:#1A5276;font-size:10px;font-weight:700;padding:2px 8px;border-radius:8px;">En crecimiento</span>'
    else:
        return '<span style="background:#FEF9E7;color:#B7770D;font-size:10px;font-weight:700;padding:2px 8px;border-radius:8px;">Zona ciega</span>'


def _bloque_camino(conteo: Counter):
    st.markdown("""
<div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
            color:#888780;font-weight:600;margin:24px 0 12px 0;">
    El camino del líder consciente
</div>
""", unsafe_allow_html=True)

    dims = list(DIMENSIONES_INTRO.items())
    col1, col2 = st.columns(2)

    for i, (nombre, datos) in enumerate(dims):
        col = col1 if i % 2 == 0 else col2

        practicas     = datos["practicas"]
        usadas        = sum(1 for p in practicas if conteo[p] > 0)
        pct           = round(usadas / len(practicas) * 100) if practicas else 0
        badge         = _badge_dimension(pct)

        pills_html = "".join([
            f'<span style="background:rgba(0,0,0,0.06);color:#26215C;font-size:10px;'
            f'padding:2px 8px;border-radius:8px;margin:2px 2px 2px 0;display:inline-block;">'
            f'{PRACTICAS_CORTOS[p]}</span>'
            for p in practicas
        ])

        bar_fill = f'width:{pct}%;background:#534AB7;height:4px;border-radius:2px;'

        with col:
            st.markdown(f"""
<div style="background:{datos['bg']};border-radius:14px;padding:18px 20px;margin-bottom:12px;
            border:1px solid #E8E6F0;">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
        <div>
            <div style="font-size:11px;color:#888780;font-weight:600;">{datos['num']}</div>
            <div style="font-size:15px;font-weight:700;color:#26215C;margin-top:2px;">
                {datos['icon']} {nombre}
            </div>
        </div>
        {badge}
    </div>
    <div style="margin-bottom:10px;">{pills_html}</div>
    <div style="background:rgba(0,0,0,0.08);border-radius:2px;height:4px;">
        <div style="{bar_fill}"></div>
    </div>
    <div style="font-size:10px;color:#888780;margin-top:4px;">{usadas}/{len(practicas)} prácticas exploradas</div>
</div>
""", unsafe_allow_html=True)


# ── Bloque 4: Accesos rápidos ─────────────────────────────────────────────────

def _bloque_accesos(conteo: Counter, eventos_desc: list):
    st.markdown("""
<div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
            color:#888780;font-weight:600;margin:24px 0 12px 0;">
    Accesos rápidos
</div>
""", unsafe_allow_html=True)

    cards = []

    # Última práctica usada
    if eventos_desc:
        key1  = eventos_desc[0]["practice_key"]
        fecha = _hace_n_dias(eventos_desc[0]["created_at"])
        usos1 = conteo[key1]
        cards.append({
            "key":   key1,
            "label": PRACTICAS_CORTOS.get(key1, key1),
            "meta":  f"{usos1} uso{'s' if usos1 != 1 else ''} · {fecha}",
            "tag":   "Reciente",
            "tag_color": "#EBF5FB",
            "tag_text":  "#1A5276",
        })

    # Segunda más usada (diferente a la primera)
    top2 = [k for k, _ in conteo.most_common() if k != (cards[0]["key"] if cards else None)]
    if top2:
        key2  = top2[0]
        usos2 = conteo[key2]
        # fecha del último uso de esta práctica
        ev2   = next((e for e in eventos_desc if e["practice_key"] == key2), None)
        fecha2 = _hace_n_dias(ev2["created_at"]) if ev2 else ""
        cards.append({
            "key":   key2,
            "label": PRACTICAS_CORTOS.get(key2, key2),
            "meta":  f"{usos2} uso{'s' if usos2 != 1 else ''} · {fecha2}",
            "tag":   "Más usada",
            "tag_color": "#F5F4FA",
            "tag_text":  "#534AB7",
        })

    # Práctica no explorada (recomendada)
    sin_explorar = [k for k in TODAS_LAS_PRACTICAS if conteo[k] == 0]
    if sin_explorar:
        key3 = sin_explorar[0]
        cards.append({
            "key":   key3,
            "label": PRACTICAS_CORTOS.get(key3, key3),
            "meta":  "Sin explorar · recomendada",
            "tag":   "Recomendada",
            "tag_color": "#FEF9E7",
            "tag_text":  "#B7770D",
        })

    if not cards:
        st.info("Completa tu primera práctica para ver accesos rápidos aquí.")
        return

    # CSS para igualar la altura de los botones en columnas
    st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {
    min-height: 80px !important;
    height: 80px !important;
    white-space: normal !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: center !important;
    padding: 12px 16px !important;
    border: 1px solid #E8E6F0 !important;
    background: white !important;
    color: #26215C !important;
    font-weight: 400 !important;
    border-radius: 12px !important;
    text-align: left !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:hover {
    border-color: #534AB7 !important;
    box-shadow: 0 4px 12px rgba(60,52,137,0.12) !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button p {
    margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)

    cols = st.columns(len(cards))
    for card, col in zip(cards, cols):
        tag_html = f'<span style="background:{card["tag_color"]};color:{card["tag_text"]};font-size:10px;font-weight:700;padding:2px 8px;border-radius:8px;">{card["tag"]}</span>'
        with col:
            if st.button(
                f"**{card['label']}**  \n{card['meta']}",
                key=f"quick_{card['key']}",
                use_container_width=True,
            ):
                st.session_state.practica_sel = card["key"]
                st.rerun()
            st.markdown(tag_html, unsafe_allow_html=True)


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    """Renderiza la página de inicio personalizada."""

    _mostrar_onboarding_tour()

    user   = st.session_state.get("user", {})
    email  = user.get("email", "")
    nombre = user.get("nombre", "") or email.split("@")[0]

    datos = _cargar_datos(email)

    _bloque_hero(nombre, datos)
    _bloque_ecosistema()
    _bloque_camino(datos["conteo"])
    _bloque_accesos(datos["conteo"], datos["eventos_desc"])
