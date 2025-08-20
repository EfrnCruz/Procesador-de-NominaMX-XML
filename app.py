"""
Aplicación Streamlit para procesar archivos XML de nómina del SAT (México)
"""
import streamlit as st
import pandas as pd
import os
from pathlib import Path
import tempfile
from xml_processor import NominaXMLProcessor
import logging
import io

# Configurar página
st.set_page_config(
    page_title="Procesador de Nómina XML - SAT México",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Procesador de Nómina XML - SAT México",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Título simple y elegante
    st.markdown("""
    <div style="text-align: center;">
        <h1>🏢 Procesador de Nómina XML - SAT México</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Descripción de la aplicación centrada
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <p style="font-size: 18px; color: #666;">
            Esta aplicación procesa archivos XML de nómina del SAT, incluyendo archivos comprimidos en ZIP.<br>
            Extrae y normaliza la información para su análisis y exportación a Excel.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para opciones
    st.sidebar.title("⚙️ Opciones de Procesamiento")
    
    # Opción 1: Seleccionar archivos
    st.sidebar.subheader("📁 Selección de Archivos")
    uploaded_files = st.sidebar.file_uploader(
        "Selecciona archivos XML o ZIP",
        type=['xml', 'zip'],
        accept_multiple_files=True,
        help="Puedes seleccionar múltiples archivos XML o ZIP"
    )
    
    # Opción 2: Ingresar ruta de directorio
    st.sidebar.subheader("📂 Ruta de Directorio")
    directory_path = st.sidebar.text_input(
        "Ruta del directorio con archivos:",
        placeholder="C:/ruta/a/tu/directorio",
        help="Ingresa la ruta completa del directorio que contiene los archivos"
    )
    
    # Botón para procesar
    process_button = st.sidebar.button("🚀 Procesar Archivos", type="primary")
    
    # Contenido principal
    if process_button:
        if not uploaded_files and not directory_path:
            st.error("⚠️ Por favor selecciona archivos o ingresa una ruta de directorio")
            return
        
        # Mostrar indicador de progreso
        with st.spinner("🔄 Procesando archivos..."):
            try:
                # Inicializar procesador
                processor = NominaXMLProcessor()
                
                # Lista para almacenar rutas de archivos
                file_paths = []
                
                # Agregar archivos subidos
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        # Guardar archivo temporalmente
                        temp_dir = tempfile.mkdtemp()
                        temp_path = os.path.join(temp_dir, uploaded_file.name)
                        
                        with open(temp_path, 'wb') as f:
                            f.write(uploaded_file.getvalue())
                        
                        file_paths.append(temp_path)
                
                # Agregar archivos del directorio
                if directory_path and os.path.exists(directory_path):
                    dir_path = Path(directory_path)
                    
                    # BÚSQUEDA INTELIGENTE: Analizar contenido de archivos en lugar de usar criterios fijos
                    st.info(f"🔍 Analizando inteligentemente el directorio: {directory_path}")
                    
                    # Función para detectar si un archivo es procesable
                    def is_processable_file(file_path: Path) -> bool:
                        """Detecta inteligentemente si un archivo es procesable"""
                        try:
                            # Verificar si es un archivo (no directorio)
                            if not file_path.is_file():
                                return False
                            
                            # Verificar tamaño mínimo (archivos muy pequeños no son procesables)
                            if file_path.stat().st_size < 50:  # Menos de 50 bytes
                                return False
                            
                            # Leer los primeros bytes para analizar el contenido
                            with open(file_path, 'rb') as f:
                                header = f.read(200)  # Leer primeros 200 bytes para mejor detección
                            
                            # Detectar XML por contenido (no por extensión)
                            if (header.startswith(b'<?xml') or 
                                header.startswith(b'<cfdi') or 
                                header.startswith(b'<Comprobante') or
                                header.startswith(b'<tfd:') or
                                header.startswith(b'<nomina12:')):
                                return True
                            
                            # Detectar ZIP por firma mágica (no por extensión)
                            if header.startswith(b'PK\x03\x04'):
                                return True
                            
                            # Detectar otros formatos procesables
                            # Buscar patrones XML en cualquier parte del header
                            xml_patterns = [b'<?xml', b'<cfdi', b'<Comprobante', b'<tfd:', b'<nomina12:']
                            if any(pattern in header for pattern in xml_patterns):
                                return True
                            
                            # Verificar si el archivo contiene XML más adelante (para archivos grandes)
                            if file_path.stat().st_size < 10000:  # Solo para archivos pequeños
                                try:
                                    with open(file_path, 'rb') as f:
                                        content = f.read()
                                        if any(pattern in content for pattern in xml_patterns):
                                            return True
                                except:
                                    pass
                            
                            return False
                            
                        except Exception as e:
                            # Silenciar errores de archivos que no se pueden leer
                            return False
                    
                    # Escanear recursivamente todo el directorio
                    all_files = []
                    xml_files = []
                    zip_files = []
                    other_processable = []
                    
                    st.write("🔍 Escaneando archivos...")
                    
                    # Progreso visual
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Obtener lista de todos los archivos en el directorio y subdirectorios
                    all_paths = list(dir_path.rglob('*'))
                    total_files = len(all_paths)
                    
                    for i, file_path in enumerate(all_paths):
                        # Actualizar progreso
                        progress = (i + 1) / total_files
                        progress_bar.progress(progress)
                        status_text.text(f"Analizando {i + 1}/{total_files}: {file_path.name}")
                        
                        if is_processable_file(file_path):
                            all_files.append(file_path)
                            
                            # Clasificar por tipo detectado
                            if file_path.suffix.lower() == '.xml' or (file_path.suffix.lower() != '.zip' and 
                                (file_path.read_bytes().startswith(b'<?xml') or 
                                 file_path.read_bytes().startswith(b'<cfdi') or 
                                 file_path.read_bytes().startswith(b'<Comprobante'))):
                                xml_files.append(file_path)
                            elif file_path.suffix.lower() == '.zip' or file_path.read_bytes().startswith(b'PK\x03\x04'):
                                zip_files.append(file_path)
                            else:
                                other_processable.append(file_path)
                    
                    # Ocultar elementos de progreso
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Mostrar resultados de la búsqueda inteligente
                    st.success(f"✅ Búsqueda inteligente completada")
                    
                    # Estadísticas detalladas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📁 XML", len(xml_files))
                    with col2:
                        st.metric("📦 ZIP", len(zip_files))
                    with col3:
                        st.metric("🔧 Otros", len(other_processable))
                    with col4:
                        st.metric("🎯 Total", len(all_files))
                    
                    # Información adicional
                    st.info(f"📊 Análisis completado: {total_files} archivos escaneados")
                    if total_files > 0:
                        efficiency = (len(all_files) / total_files) * 100
                        st.info(f"🎯 Eficiencia de detección: {efficiency:.1f}% ({len(all_files)}/{total_files})")
                    
                    # Mostrar lista detallada de archivos encontrados
                    if all_files:
                        st.write("📋 Archivos procesables detectados:")
                        
                        # Agrupar por tipo para mejor visualización
                        if xml_files:
                            st.write("  📄 **Archivos XML:**")
                            for file in xml_files:
                                st.write(f"    • {file.name} ({file.parent.name})")
                        
                        if zip_files:
                            st.write("  📦 **Archivos ZIP:**")
                            for file in zip_files:
                                st.write(f"    • {file.name} ({file.parent.name})")
                        
                        if other_processable:
                            st.write("  🔧 **Otros archivos procesables:**")
                            for file in other_processable:
                                st.write(f"    • {file.name} ({file.parent.name})")
                        
                        # Agregar todos los archivos procesables a la lista
                        file_paths.extend([str(f) for f in all_files])
                        
                    else:
                        st.warning("⚠️ No se encontraron archivos procesables en el directorio")
                        st.write("💡 La búsqueda inteligente analizó el contenido de todos los archivos")
                        st.write("💡 Tipos de archivos que puede detectar:")
                        st.write("  • Archivos XML (por contenido)")
                        st.write("  • Archivos ZIP (por firma)")
                        st.write("  • Cualquier archivo que contenga XML válido")
                elif directory_path:
                    st.error(f"❌ El directorio no existe: {directory_path}")
                    return
                
                if not file_paths:
                    st.error("❌ No se encontraron archivos para procesar")
                    return
                
                # Mostrar archivos encontrados
                st.info(f"📋 Se encontraron {len(file_paths)} archivos para procesar")
                
                # Procesar archivos
                df = processor.process_multiple_files(file_paths)
                
                if df.empty:
                    st.error("❌ No se pudieron procesar los archivos o están vacíos")
                    return
                
                # Mostrar resultados
                st.success(f"✅ Se procesaron {len(df)} registros de nómina exitosamente")
                
                # Mostrar estadísticas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Registros", len(df))
                with col2:
                    st.metric("Total de Archivos", len(file_paths))
                with col3:
                    st.metric("Columnas de Datos", len(df.columns))
                
                # Mostrar vista previa de datos
                st.subheader("👀 Vista Previa de Datos")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Mostrar información de columnas
                with st.expander("📊 Ver Información de Columnas"):
                    col_info = pd.DataFrame({
                        'Columna': df.columns,
                        'Tipo': df.dtypes.astype(str),
                        'Valores Únicos': df.nunique(),
                        'Valores Nulos': df.isnull().sum()
                    })
                    st.dataframe(col_info, use_container_width=True)
                
                # Opciones de exportación
                st.subheader("💾 Exportar Datos")
                
                # Crear buffer de Excel en memoria
                try:
                    with st.spinner("🔄 Generando archivo Excel..."):
                        # Crear buffer de bytes para Excel
                        output = io.BytesIO()
                        
                        # Usar ExcelWriter con el buffer
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Nómina Consolidada', index=False)
                            
                            # Ajustar ancho de columnas
                            worksheet = writer.sheets['Nómina Consolidada']
                            for column in worksheet.columns:
                                max_length = 0
                                column_letter = column[0].column_letter
                                for cell in column:
                                    try:
                                        if len(str(cell.value)) > max_length:
                                            max_length = len(str(cell.value))
                                    except:
                                        pass
                                adjusted_width = min(max_length + 2, 50)
                                worksheet.column_dimensions[column_letter].width = adjusted_width
                        
                        # Obtener bytes del buffer
                        excel_bytes = output.getvalue()
                        output.close()
                        
                        # Botón de descarga
                        st.download_button(
                            label="📁 Descargar Excel",
                            data=excel_bytes,
                            file_name="nomina_consolidada.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_excel"
                        )
                        
                        st.success("✅ Archivo Excel generado exitosamente")
                        
                except Exception as e:
                    st.error(f"❌ Error generando Excel: {str(e)}")
                    logger.error(f"Error en Excel: {e}")
                
                # Mostrar datos completos con paginación
                st.subheader("📋 Datos Completos")
                
                # Agregar controles de paginación
                page_size = st.selectbox("Registros por página:", [10, 25, 50, 100], index=0)
                total_pages = (len(df) + page_size - 1) // page_size
                
                if total_pages > 1:
                    page = st.selectbox("Página:", range(1, total_pages + 1), index=0) - 1
                else:
                    page = 0
                
                start_idx = page * page_size
                end_idx = min(start_idx + page_size, len(df))
                
                st.write(f"Mostrando registros {start_idx + 1} a {end_idx} de {len(df)}")
                st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True)
                
                # Limpiar archivos temporales
                if uploaded_files:
                    for temp_path in file_paths:
                        try:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                                os.rmdir(os.path.dirname(temp_path))
                        except:
                            pass
                
                st.success("✅ Procesamiento completado exitosamente")
                
            except Exception as e:
                st.error(f"❌ Error durante el procesamiento: {str(e)}")
                logger.error(f"Error en procesamiento: {e}")
    
    # Footer con copyright
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 10px; color: #888; font-size: 12px;">
        © Efren Cruz - <a href="https://nominante.com" target="_blank" style="color: #888; text-decoration: none;">nominante.com</a> | Desarrollado con ❤️ para la comunidad nominista de México
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
