import streamlit as st
import pandas as pd
from xml_handler import NominaXMLHandler
import io
import estilos

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Nomina')
    processed_data = output.getvalue()
    return processed_data

def main():
    # 1. Configuración de estilo corporativo
    estilos.setup_app_style(
        page_title="Procesador de Nómina (V3)",
        page_icon="💸"
    )

    # 2. Header Principal
    estilos.create_main_header(
        "💸 Procesador de XML de Nómina",
        "Sat Nomina 1.2 - Normalización y Reporte Corporativo"
    )

    # 3. Sidebar (Eliminada zona de carga lateral exclusiva, ahora es central/tabs)
    estilos.create_sidebar_header()
    st.sidebar.info("Versión 3.1 - Corporativa\n\nSoporte para Carpeta Local y ZIPs")
    
    # 4. Área Principal
    estilos.create_section_header("Carga y Procesamiento", "📥")

    tab1, tab2 = st.tabs(["📂 Cargar Archivos", "💻 Carpeta Local"])
    
    df = pd.DataFrame() # Initialize empty DF

    with tab1:
        uploaded_files = st.file_uploader(
            "Selecciona archivos XML", 
            type=['xml'], 
            accept_multiple_files=True,
            help="Selecciona uno o más archivos XML de nómina."
        )
        if uploaded_files:
            estilos.info_message(f"📂 **{len(uploaded_files)}** archivos listos.")
            if st.button("🚀 Procesar Archivos (Subida)", type="primary"):
                with st.spinner("Procesando archivos subidos..."):
                    handler = NominaXMLHandler()
                    df = handler.process_files(uploaded_files)

    with tab2:
        st.markdown("Ingresa la ruta absoluta de la carpeta que contiene tus archivos XML o ZIPs.")
        local_path = st.text_input("Ruta de la carpeta local", placeholder="ej. C:\\Documentos\\Nominas2024")
        
        if local_path:
            import os
            if os.path.exists(local_path):
                if st.button("🚀 Escanear y Procesar Carpeta", type="primary"):
                    with st.spinner(f"Escaneando {local_path} (incluyendo ZIPs)..."):
                        handler = NominaXMLHandler()
                        # Scan
                        found_files = handler.scan_directory(local_path)
                        
                        if found_files:
                            st.toast(f"Se encontraron {len(found_files)} archivos XML.", icon="✅")
                            df = handler.process_files(found_files)
                        else:
                            estilos.warning_message("No se encontraron archivos XML o ZIPs válidos en esta ruta.")
            else:
                estilos.error_message("❌ La ruta especificada no existe.")
                
    # Resultados compartidos
    if not df.empty:
        st.markdown("---")
        estilos.create_section_header("Resultados", "📊")
        estilos.success_message("✅ Procesamiento completado exitosamente")
        
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            estilos.styled_metric("Registros", len(df))
        with col2:
            estilos.styled_metric("Columnas", len(df.columns))
        with col3:
            if 'Total' in df.columns:
                estilos.styled_metric("Total Pagado", f"${df['Total'].sum():,.2f}")
            else:
                estilos.styled_metric("Total Pagado", "$0.00")

        # Vista Previa
        st.subheader("Vista Previa de Datos")
        st.dataframe(df.head(50), use_container_width=True)
        
        # Descarga
        excel_data = to_excel(df)
        st.download_button(
            label="📥 Descargar Reporte Excel",
            data=excel_data,
            file_name="Reporte_Nomina_V3.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        
    # Footer
    estilos.create_footer(
        "Sistema de Nómina Corporativo",
        "Herramienta interna para procesamiento de CFDI de Nómina",
        "✨ V3.0 | Estilos Corporativos | Ordenamiento Inteligente"
    )

if __name__ == "__main__":
    main()
