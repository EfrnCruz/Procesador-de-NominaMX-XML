# 📋 Planificación: Aplicación de Procesamiento de XML de Nómina México

## 🎯 Visión del Proyecto
Desarrollar una aplicación web con Streamlit para procesar archivos XML de nómina del SAT (México), incluyendo archivos comprimidos en ZIP, normalizar la información y exportar a Excel.

## 🏗️ Arquitectura del Sistema

### Componentes Principales
1. **Interfaz de Usuario (Streamlit)**
   - Selección de archivos XML/ZIP
   - Visualización de datos procesados
   - Descarga de resultados en Excel

2. **Procesador de XML**
   - Parser de archivos XML de nómina
   - Extracción de datos estructurados
   - Normalización de información

3. **Gestor de Archivos**
   - Procesamiento de archivos ZIP
   - Manejo de múltiples archivos XML
   - Validación de formatos

4. **Exportador de Datos**
   - Generación de Excel con datos normalizados
   - Estructura de columnas optimizada
   - Formato de descarga

## 📊 Estructura de Datos a Extraer

### Datos del Patrón
- RFC, Nombre, Régimen Fiscal
- Registro Patronal

### Datos del Trabajador
- RFC, Nombre, CURP, NSS
- Información laboral y salarial
- Ubicación y departamento

### Conceptos (Percepciones, Deducciones, Otros Pagos)
- Tipo y concepto
- Importes gravados y exentos
- Claves y descripciones

## 🔄 Flujo de Procesamiento
1. Selección/entrada de archivos
2. Descompresión de ZIP (si aplica)
3. Parsing de XML individuales
4. Normalización y estructuración de datos
5. Consolidación en DataFrame
6. Exportación a Excel
7. Descarga del archivo

## 🛠️ Tecnologías
- **Frontend**: Streamlit
- **Procesamiento**: Python, xml.etree.ElementTree
- **Manipulación de datos**: pandas, openpyxl
- **Archivos**: zipfile, pathlib
