# 🏢 Procesador de Nómina XML - SAT México

Aplicación web desarrollada con Streamlit para procesar archivos XML de nómina del SAT (México), incluyendo archivos comprimidos en ZIP, normalizar la información y exportar a Excel.

## 🚀 Características

- **Procesamiento de múltiples formatos**: XML individuales y archivos ZIP
- **Extracción automática de datos**: Patrón, trabajador, percepciones, deducciones y otros pagos
- **Normalización inteligente**: Conversión de conceptos dinámicos a columnas estructuradas
- **Exportación a Excel**: Archivo optimizado con formato automático
- **Interfaz intuitiva**: Aplicación web fácil de usar con Streamlit
- **Búsqueda inteligente**: Análisis automático del contenido de archivos
- **Extracción de UUID**: Identificación única de cada CFDI para trazabilidad
- **Catálogo unificado**: Columnas consistentes entre todos los registros

## 📋 Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

## 🛠️ Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd procesador-nomina-xml
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Uso

### Ejecutar la aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador web en `http://localhost:8501`

### Flujo de trabajo

1. **Seleccionar archivos**: Usa el selector para subir archivos XML o ZIP
2. **O especificar directorio**: Escribe la ruta del directorio con archivos
3. **Procesar**: Haz clic en "Procesar Archivos"
4. **Revisar resultados**: Visualiza los datos extraídos
5. **Exportar**: Descarga el archivo Excel consolidado

## 📊 Estructura de Datos Extraídos

### Datos del Patrón
- RFC, Nombre, Régimen Fiscal
- Registro Patronal

### Datos del Trabajador
- RFC, Nombre, CURP, NSS
- Información laboral y salarial
- Ubicación y departamento

### Conceptos Dinámicos
- **Percepciones**: Concepto_ImporteGravado, Concepto_ImporteExento
- **Deducciones**: Concepto_Importe
- **Otros Pagos**: Concepto_Importe

### Identificación Única
- **CFDI_UUID**: UUID único de cada CFDI para trazabilidad

## 🔧 Estructura del Proyecto

```
procesador-nomina-xml/
├── app.py                 # Aplicación principal Streamlit
├── xml_processor.py      # Módulo de procesamiento XML
├── requirements.txt      # Dependencias del proyecto
├── README.md            # Este archivo
├── PLANNING.md          # Planificación del proyecto
```

## 📁 Tipos de Archivos Soportados

- **XML individuales**: Archivos XML de nómina del SAT
- **Archivos ZIP**: Contenedores con múltiples XMLs
- **Directorios**: Carpetas con archivos XML/ZIP
- **Búsqueda inteligente**: Detecta archivos por contenido, no por extensión

## 🎯 Casos de Uso

- **Contadores**: Procesamiento masivo de nóminas para análisis fiscal
- **Recursos Humanos**: Consolidación de información de empleados
- **Auditoría**: Revisión de datos de nómina en formato estructurado
- **Reportes**: Generación de reportes consolidados para autoridades
- **Trazabilidad**: Identificación única de recibos para control de cancelaciones

## 🐛 Solución de Problemas

### Error de dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Error de permisos (Windows)
Ejecutar PowerShell como administrador

### Error de memoria
Reducir el número de archivos procesados simultáneamente

## 📝 Notas Técnicas

- **Namespaces XML**: La aplicación maneja automáticamente los namespaces del SAT
- **Procesamiento dinámico**: Las columnas se crean automáticamente según los conceptos encontrados
- **Manejo de errores**: Logging detallado para debugging
- **Limpieza automática**: Los archivos temporales se eliminan automáticamente
- **Búsqueda inteligente**: Análisis de contenido para detectar archivos procesables
- **Catálogo unificado**: Sistema de dos pasadas para columnas consistentes
- **Extracción UUID**: Múltiples estrategias para obtener UUID de cada CFDI

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT** - ver el archivo [`LICENSE`](LICENSE) para más detalles.

### ¿Por qué Open Source?

Este proyecto se desarrolla como **software open source** para:
- **Beneficiar a la comunidad nominista** de México
- **Permitir mejoras colaborativas** del código
- **Facilitar la adopción** en diferentes entornos
- **Promover la transparencia** en el desarrollo de software

## 📞 Soporte

Para soporte técnico o preguntas, por favor abre un issue en el repositorio.

---

## 👨‍💻 **Desarrolladores**

- **Efren Cruz** - Desarrollador principal y experto en nóminas
- **Claude Sonnet 4** - Asistente AI para desarrollo y optimización

## 🌐 **Recursos del Desarrollador**

- **Sitio Web**: [nominante.com](https://nominante.com)
- **Especialización**: Soluciones para nóminas
- **Contacto**: Para soporte técnico o consultas comerciales, visita [nominante.com](https://nominante.com)

**Desarrollado con ❤️ para la comunidad nominista de México**

**© Efren Cruz - nominante.com**

