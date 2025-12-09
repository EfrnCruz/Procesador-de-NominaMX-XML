import streamlit as st

def setup_app_style(page_title="Mi App", page_icon="📂", layout="wide"):
    """
    Configura el estilo corporativo estándar para cualquier aplicación Streamlit
    """
    # Configuración de página
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )

    # CSS corporativo
    st.markdown("""
    <style>
        /* Paleta de Colores Corporativa */
        :root {
            --verde-principal: #06752e;
            --verde-claro: #1a7f37;
            --verde-oscuro: #0a8c3d;
            --fondo-oscuro: #0d1117;
            --fondo-semi-transparente: rgba(13, 17, 23, 0.8);
            --fondo-transparente: rgba(13, 17, 23, 0.6);
            --texto-principal: #e6edf3;
            --texto-secundario: #c9d1d9;
            --exito-verde: #1a7f37;
            --advertencia-amarillo: #ffc107;
            --error-rojo: #dc3545;
        }

        /* Reset general */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        /* Header Principal */
        .main-header {
            background: linear-gradient(135deg, #0d1117 0%, #06752e 50%, #0d1117 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(6, 117, 46, 0.3);
            border: 1px solid rgba(6, 117, 46, 0.3);
        }

        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            color: #ffffff;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        .main-header p {
            color: #c9d1d9;
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
        }

        .sub-header {
            color: #c9d1d9;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }

        /* Sidebar Header */
        .sidebar-header {
            background: linear-gradient(135deg, #0d1117 0%, #06752e 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            border: 1px solid rgba(6, 117, 46, 0.3);
        }

        /* Tarjetas de Estadísticas */
        .stats-card {
            background: rgba(13, 17, 23, 0.8);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            margin: 0.5rem 0;
            border-left: 4px solid #06752e;
            color: #c9d1d9;
        }

        /* Cajas de Mensajes */
        .success-box {
            background-color: rgba(26, 127, 55, 0.15);
            border: 1px solid #1a7f37;
            border-radius: 6px;
            padding: 1rem;
            margin: 1rem 0;
            color: #1a7f37;
        }

        .warning-box {
            background-color: rgba(255, 193, 7, 0.15);
            border: 1px solid #ffc107;
            border-radius: 6px;
            padding: 1rem;
            margin: 1rem 0;
            color: #ffc107;
        }

        .error-box {
            background-color: rgba(220, 53, 69, 0.15);
            border: 1px solid #dc3545;
            border-radius: 6px;
            padding: 1rem;
            margin: 1rem 0;
            color: #dc3545;
        }

        .info-box {
            background-color: rgba(13, 17, 23, 0.8);
            border: 1px solid rgba(6, 117, 46, 0.3);
            border-radius: 6px;
            padding: 1rem;
            margin: 1rem 0;
            color: #e6edf3;
        }

        /* Botones */
        .stButton > button {
            background-color: #06752e !important;
            color: white !important;
            border: 1px solid #06752e !important;
            border-radius: 6px !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
            padding: 0.5rem 1.5rem !important;
        }

        .stButton > button:hover {
            background-color: #0a8c3d !important;
            border-color: #0a8c3d !important;
            box-shadow: 0 2px 8px rgba(6, 117, 46, 0.4) !important;
            transform: translateY(-1px) !important;
        }

        .stDownloadButton > button {
            background-color: #06752e !important;
            color: white !important;
            border: 1px solid #06752e !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }

        .stDownloadButton > button:hover {
            background-color: #0a8c3d !important;
            border-color: #0a8c3d !important;
            box-shadow: 0 2px 8px rgba(6, 117, 46, 0.4) !important;
            transform: translateY(-1px) !important;
        }

        /* Métricas */
        .stMetric {
            background-color: rgba(13, 17, 23, 0.8) !important;
            border: 1px solid rgba(6, 117, 46, 0.3) !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        }

        .stMetric > div > div > div > div > div {
            color: #1a7f37 !important;
            font-weight: bold !important;
        }

        .stMetric > div > div > div > div > div > div {
            color: #c9d1d9 !important;
            font-weight: bold !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(13, 17, 23, 0.8) !important;
            border-radius: 8px !important;
            border: 1px solid rgba(6, 117, 46, 0.3) !important;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: rgba(6, 117, 46, 0.2) !important;
            color: #e6edf3 !important;
            border-radius: 6px !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(6, 117, 46, 0.4) !important;
        }

        /* File Uploader */
        .stFileUploader {
            border: 2px dashed rgba(6, 117, 46, 0.5) !important;
            border-radius: 8px !important;
            background-color: rgba(13, 17, 23, 0.4) !important;
        }

        /* Sliders */
        .stSlider > div > div > div {
            background-color: #06752e !important;
        }

        /* Selectbox y otros inputs */
        .stSelectbox > div > div > div {
            background-color: rgba(13, 17, 23, 0.8) !important;
            border: 1px solid rgba(6, 117, 46, 0.3) !important;
            color: #e6edf3 !important;
        }

        /* DataFrames */
        .stDataFrame {
            background-color: rgba(13, 17, 23, 0.8) !important;
            border: 1px solid rgba(6, 117, 46, 0.3) !important;
            border-radius: 8px !important;
        }

        .dataframe-container {
            border-radius: 8px !important;
            overflow: hidden !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: rgba(13, 17, 23, 0.6) !important;
            border-radius: 6px !important;
            border: 1px solid rgba(6, 117, 46, 0.2) !important;
        }

        /* Progress bar */
        .stProgress > div > div > div > div {
            background-color: #06752e !important;
        }

        /* Footer */
        .footer {
            text-align: center;
            color: #e6edf3;
            padding: 20px;
            border-top: 1px solid rgba(6, 117, 46, 0.3);
            background: rgba(13, 17, 23, 0.8);
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            margin-top: 2rem;
        }

        /* Textos generales */
        h1, h2, h3, h4, h5, h6 {
            color: #e6edf3 !important;
        }

        .stMarkdown {
            color: #c9d1d9 !important;
        }

        .element-container {
            background-color: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)

def create_main_header(title, subtitle=""):
    """Crea un header principal con estilo corporativo"""
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def create_sidebar_header(title="⚙️ Configuración"):
    """Crea un header consistente para sidebar"""
    st.sidebar.markdown(f"""
    <div class="sidebar-header">
        <h2 style="margin: 0; font-size: 1.2em;">{title}</h2>
    </div>
    """, unsafe_allow_html=True)

def create_section_header(title, icon="📁"):
    """Crea un header de sección consistente"""
    st.markdown(f"""
    <div style='background: rgba(13, 17, 23, 0.6); border: 1px solid rgba(6, 117, 46, 0.3);
                padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
        <h2 style='color: #1a7f37; margin-top: 0; margin-bottom: 1rem;'>{icon} {title}</h2>
    </div>
    """, unsafe_allow_html=True)

def success_message(message):
    """Crea un mensaje de éxito consistente"""
    st.markdown(f"""
    <div class="success-box">
        ✅ <strong>{message}</strong>
    </div>
    """, unsafe_allow_html=True)

def warning_message(message):
    """Crea un mensaje de advertencia consistente"""
    st.markdown(f"""
    <div class="warning-box">
        ⚠️ <strong>{message}</strong>
    </div>
    """, unsafe_allow_html=True)

def error_message(message):
    """Crea un mensaje de error consistente"""
    st.markdown(f"""
    <div class="error-box">
        ❌ <strong>{message}</strong>
    </div>
    """, unsafe_allow_html=True)

def info_message(message):
    """Crea un mensaje de información consistente"""
    st.markdown(f"""
    <div class="info-box">
        ℹ️ <strong>{message}</strong>
    </div>
    """, unsafe_allow_html=True)

def create_footer(app_name, description, features=""):
    """Crea un footer consistente"""
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        <p style="font-size: 1.1em; margin-bottom: 10px;">🏢 <strong style="color: #1a7f37;">{app_name}</strong></p>
        <p style="color: #c9d1d9; margin: 5px 0;">{description}</p>
        {f'<p style="color: #1a7f37; font-weight: 500; margin-top: 10px;">{features}</p>' if features else ''}
    </div>
    """, unsafe_allow_html=True)

def styled_metric(label, value, delta=None, help_text=None):
    """Crea una métrica con estilo corporativo"""
    return st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text
    )

def create_corporate_app(app_name, app_description):
    """
    Función template básica para cualquier aplicación con estilo corporativo
    """
    # Configurar estilo
    setup_app_style(
        page_title=app_name,
        page_icon="📂"
    )

    # Header principal
    create_main_header(
        title=f"📂 {app_name}",
        subtitle=app_description
    )

    # Sidebar
    create_sidebar_header()
