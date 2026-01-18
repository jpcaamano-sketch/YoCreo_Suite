"""
Estilos CSS unificados para YoCreo Suite
Tipografía: Inter
Colores: Naranja #F26B3A, Morado #5B2D90
"""

def get_css():
    """Retorna el CSS completo de la aplicación"""
    return """
    <style>
        /* Importar fuente Inter de Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Aplicar Inter a toda la app */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Ocultar elementos de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {display: none !important;}

        /* Ocultar botón X del sidebar */
        [data-testid="stSidebar"] button {display: none !important;}

        /* Espaciado del contenedor principal */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Estilo para títulos */
        h1 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: #5B2D90;
        }

        h2, h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            color: #333333;
        }

        /* Botón primario con color naranja marca */
        .stButton > button[kind="primary"] {
            background-color: #F26B3A;
            border-color: #F26B3A;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #D85A2D;
            border-color: #D85A2D;
        }

        /* Estilo para selectbox y text inputs */
        .stSelectbox, .stTextInput, .stTextArea {
            font-family: 'Inter', sans-serif;
        }

        /* Estilo para expanders */
        .streamlit-expanderHeader {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }

        /* Alertas y mensajes */
        .stAlert {
            font-family: 'Inter', sans-serif;
            margin-bottom: 1rem;
        }

        /* Estilo para tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }

        /* Divider personalizado */
        hr {
            border: none;
            border-top: 1px solid #E0E0E0;
            margin: 1.5rem 0;
        }

        /* Caption estilo */
        .stCaption {
            font-family: 'Inter', sans-serif;
            color: #666666;
        }
    </style>
    """


def apply_styles(st):
    """Aplica los estilos CSS a la página de Streamlit"""
    st.markdown(get_css(), unsafe_allow_html=True)


def show_logo(st, width=100):
    """Muestra el logo alineado a la derecha"""
    col1, col2 = st.columns([6, 1])
    with col2:
        st.image("assets/logo.png", width=width)


def show_header(st, titulo, subtitulo, icono=""):
    """Muestra el header estándar de una práctica"""
    show_logo(st)
    st.title(f"{icono} {titulo}")
    st.caption(subtitulo)
    st.divider()
