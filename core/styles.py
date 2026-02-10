"""
Estilos CSS unificados para YoCreo Suite
Protocolo Estandar v3.0
- Sidebar oscuro con logo
- Fondo gris claro
- Contenido en tarjeta blanca
"""

import streamlit.components.v1 as components


def get_css():
    """Retorna el CSS completo segun protocolo estandar"""
    return """
    <style>
        /* Importar fuente Inter de Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Aplicar Inter a toda la app */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        /* Fondo General: Violeta suave */
        .stApp {
            background-color: rgba(78, 50, 173, 0.2) !important;
        }

        /* Ocultar elementos de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {display: none !important;}

        /* Ocultar "Press Enter to submit form" */
        [data-testid="InputInstructions"] {
            display: none !important;
        }

        /* Ocultar boton X del sidebar */
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {display: none !important;}

        /* Espaciado del contenedor principal */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 800px;
        }

        /* Contenedor exterior: transparente */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 0 !important;
            margin-bottom: 0 !important;
            box-shadow: none !important;
        }

        /* Contenedores internos (st.container(border=True)): Tarjeta blanca con sombra */
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 28px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
        }

        /* Titulos */
        h1, h2, h3, h4 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            color: #1a1a2e !important;
        }

        h1 {
            font-size: 28px !important;
        }

        h2 {
            font-size: 22px !important;
        }

        /* Subtitulo descriptivo */
        .descripcion-practica {
            color: #6c757d !important;
            font-size: 15px !important;
            margin-top: -8px !important;
            margin-bottom: 20px !important;
        }

        /* Boton de Accion */
        div.stButton > button {
            background-color: #FF6B4E !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.85rem 1.5rem !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(255, 107, 78, 0.3) !important;
            transition: all 0.2s ease !important;
        }

        div.stButton > button:hover {
            background-color: #E5553A !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(255, 107, 78, 0.4) !important;
        }

        /* Boton de Descarga: Gris oscuro */
        div.stDownloadButton > button {
            background-color: #2D3436 !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.85rem 1.5rem !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            transition: all 0.2s ease !important;
        }

        div.stDownloadButton > button:hover {
            background-color: #1a1a2e !important;
            transform: translateY(-2px) !important;
        }

        /* Labels de campos */
        .stTextInput label, .stSelectbox label, .stTextArea label, .stSlider label {
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            color: #2D3436 !important;
            margin-bottom: 4px !important;
        }

        /* Inputs y TextAreas */
        .stTextInput input, .stTextArea textarea {
            font-family: 'Inter', sans-serif !important;
            border-radius: 10px !important;
            border: 1px solid #E0E0E0 !important;
            padding: 12px !important;
            font-size: 14px !important;
            background-color: #FAFAFA !important;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #FF6B4E !important;
            box-shadow: 0 0 0 2px rgba(255, 107, 78, 0.15) !important;
            background-color: #FFFFFF !important;
        }

        /* Selectbox */
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 10px !important;
        }

        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 10px !important;
            border: 1px solid #E0E0E0 !important;
            background-color: #FAFAFA !important;
        }

        /* Expander */
        .streamlit-expanderHeader {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            color: #2D3436 !important;
            background-color: #F8F9FA !important;
            border-radius: 10px !important;
        }

        /* Divider */
        hr {
            border: none !important;
            border-top: 1px solid #E8E8E8 !important;
            margin: 1.5rem 0 !important;
        }

        /* Alertas personalizadas */
        .custom-warning {
            background-color: #FFF8E1;
            color: #F57C00;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #F57C00;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
        }

        .custom-error {
            background-color: #FFEBEE;
            color: #C62828;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #C62828;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
        }

        .custom-success {
            background-color: #E8F5E9;
            color: #2E7D32;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #2E7D32;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
        }

        .custom-info {
            background-color: #E3F2FD;
            color: #1565C0;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #1565C0;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
        }

        /* ========== SIDEBAR OSCURO ========== */

        /* Sidebar general - Fondo violeta */
        [data-testid="stSidebar"] {
            background-color: rgba(78, 50, 173, 0.8) !important;
            box-shadow: 4px 0 15px rgba(0, 0, 0, 0.3) !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            background-color: rgba(78, 50, 173, 0.8) !important;
            padding-top: 0.5rem !important;
        }

        /* Quitar bordes de contenedores en sidebar */
        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
        }

        /* Logo en sidebar */
        .sidebar-logo {
            text-align: left;
            padding: 0 0 35px 16px;
            margin-top: -10px;
        }

        .sidebar-logo img {
            max-width: 80px;
            height: auto;
        }

        /* Categoria titulo en sidebar - Texto claro */
        .cat-title {
            font-family: 'Hiragino Kaku Gothic Std', 'Hiragino Sans', sans-serif !important;
            font-size: 10px !important;
            font-weight: 700 !important;
            color: #95A5A6 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            margin: 0 0 0 10px !important;
            padding: 0 0 25px 0 !important;
            display: flex !important;
            align-items: center !important;
            min-height: 20px !important;
        }

        /* Separador en sidebar */
        .sidebar-divider {
            border: none;
            border-top: 1px solid #4a4a4a;
            margin: 20px 10px !important;
        }

        /* Forzar espaciado compacto en sidebar */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
            margin-bottom: 0 !important;
        }

        /* Botones menu en sidebar - Texto blanco */
        [data-testid="stSidebar"] .stButton {
            margin: 0 !important;
            padding: 0 !important;
        }

        [data-testid="stSidebar"] .stButton > button {
            background-color: transparent !important;
            color: #FFFFFF !important;
            border: none !important;
            border-left: 3px solid transparent !important;
            border-radius: 0 !important;
            padding: 0 10px 0 24px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 400 !important;
            font-size: 10px !important;
            text-align: left !important;
            justify-content: flex-start !important;
            align-items: center !important;
            box-shadow: none !important;
            margin: 0 0 10px 0 !important;
            min-height: 20px !important;
            height: 20px !important;
            line-height: 20px !important;
            transform: scale(0.75) !important;
            transform-origin: left center !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stSidebar"] .stButton > button p,
        [data-testid="stSidebar"] .stButton > button span,
        [data-testid="stSidebar"] .stButton > button div {
            text-align: left !important;
            width: 100% !important;
            color: #FFFFFF !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-left: 3px solid #E67E22 !important;
            transform: none !important;
        }

        /* Item seleccionado en sidebar */
        [data-testid="stSidebar"] .menu-item-selected > button {
            background-color: rgba(230, 126, 34, 0.2) !important;
            border-left: 3px solid #E67E22 !important;
            font-weight: 600 !important;
        }

        [data-testid="stSidebar"] .block-container {
            padding: 0 !important;
        }

        /* Indicadores de seleccion en sidebar */
        .indicador-sel {
            color: #E67E22 !important;
            font-size: 8px !important;
            margin-right: 8px !important;
        }

        .indicador {
            color: transparent !important;
            font-size: 8px !important;
            margin-right: 8px !important;
        }

        /* Reducir gap entre columnas en sidebar */
        [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
            gap: 0 !important;
            margin-bottom: -6px !important;
        }

        /* Espaciado uniforme entre elementos */
        [data-testid="stSidebar"] .element-container {
            margin-bottom: 2px !important;
            padding: 0 !important;
        }

        /* Boton de manual en contenido principal */
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-child .stButton button {
            background-color: #2D3436 !important;
            color: white !important;
            border: none !important;
            border-radius: 50% !important;
            width: 32px !important;
            height: 32px !important;
            min-height: 32px !important;
            padding: 0 !important;
            font-size: 14px !important;
            font-weight: bold !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]:first-child .stButton button:hover {
            background-color: #1a1a2e !important;
            transform: scale(1.1) !important;
        }

        /* Slider */
        .stSlider > div > div > div {
            background-color: #E67E22 !important;
        }
    </style>
    """


def get_anti_autocomplete_script():
    """Retorna script JS para desactivar autocompletado"""
    return """
    <script>
        function disableAutocomplete() {
            const inputs = window.parent.document.querySelectorAll('input, textarea');
            inputs.forEach(input => {
                input.setAttribute('autocomplete', 'off');
                input.setAttribute('spellcheck', 'false');
            });
        }
        window.addEventListener('load', disableAutocomplete);
        setInterval(disableAutocomplete, 1000);
    </script>
    """


def get_remember_page_script():
    """Script para recordar la ultima pagina visitada"""
    return """
    <script>
        // Guardar pagina actual en localStorage
        const urlParams = new URLSearchParams(window.parent.location.search);
        const currentPage = urlParams.get('p');
        if (currentPage) {
            localStorage.setItem('yocreo_last_page', currentPage);
        }

        // Si no hay parametro p y hay pagina guardada, redirigir
        if (!currentPage) {
            const savedPage = localStorage.getItem('yocreo_last_page');
            if (savedPage && savedPage !== 'introduccion') {
                const newUrl = window.parent.location.pathname + '?p=' + savedPage;
                window.parent.location.href = newUrl;
            }
        }
    </script>
    """


def apply_styles(st):
    """Aplica los estilos CSS y scripts"""
    st.markdown(get_css(), unsafe_allow_html=True)
    components.html(get_anti_autocomplete_script(), height=0, width=0)
    components.html(get_remember_page_script(), height=0, width=0)


def show_custom_alert(st, message, alert_type="warning"):
    """Muestra alerta HTML personalizada sin iconos"""
    st.markdown(f'<div class="custom-{alert_type}">{message}</div>', unsafe_allow_html=True)
