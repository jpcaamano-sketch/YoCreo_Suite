"""
Introduccion - YoCreo Suite
Protocolo Estandar v2.0
"""

import streamlit as st
import streamlit.components.v1 as components
from core.config import PRACTICAS


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


def render():
    """Renderiza la introduccion de la Suite."""
    info = PRACTICAS["introduccion"]

    # Tour de bienvenida para nuevos usuarios (se muestra una sola vez)
    _mostrar_onboarding_tour()

    with st.container(border=True):
        st.markdown(f"### {info['titulo']}")

        st.markdown("""
        <div style="font-size: 16px; line-height: 1.8; color: #333; text-align: justify; padding: 10px 0;">
            Puedes concebir la <strong style="color: #4E32AD;">'Suite Liderazgo Consciente'</strong> como un ecosistema dual:
            por un lado, un set práctico de herramientas; por el otro, un camino de evolución personal.
        </div>

        <div style="font-size: 16px; line-height: 1.8; color: #333; text-align: justify; padding: 10px 0;">
            Un viaje que va desde el <strong style="color: #FF6B4E;">dominio interior</strong> (autogestión),
            pasando por la <strong style="color: #FF6B4E;">excelencia con otros</strong> (coordinación),
            hasta alcanzar la <strong style="color: #FF6B4E;">maestría en la visión estratégica</strong>.
        </div>
        """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### El Camino del Lider Consciente")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **1. Autogestión y Foco**
            - Priorizar con claridad
            - Presentar con impacto

            **2. Coordinación Impecable**
            - Pedir con precisión
            - Delegar con inteligencia
            - Comunicar con diplomacia
            - Cumplir compromisos
            """)

        with col2:
            st.markdown("""
            **3. Desarrollo de Otros**
            - Escuchar activamente
            - Preguntar con profundidad
            - Dar feedback constructivo
            - Evaluar con justicia

            **4. Estrategia y Relaciones**
            - Definir objetivos claros
            - Planificar reuniones efectivas
            - Negociar con maestría
            - Reparar vínculos
            """)
