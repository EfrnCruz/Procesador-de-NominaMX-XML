"""
Módulo para procesar archivos XML de nómina del SAT (México)
"""
import xml.etree.ElementTree as ET
import pandas as pd
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import logging
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NominaXMLProcessor:
    """Procesador de archivos XML de nómina del SAT"""
    
    def __init__(self):
        # Namespaces más flexibles para manejar variaciones
        self.namespaces = {
            'cfdi': 'http://www.sat.gob.mx/cfd/4',
            'nomina12': 'http://www.sat.gob.mx/nomina12',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }
        
        # Catálogo unificado de conceptos para mantener consistencia de columnas
        self.conceptos_percepciones: Set[str] = set()
        self.conceptos_deducciones: Set[str] = set()
        self.conceptos_otros_pagos: Set[str] = set()
    
    def _convert_to_numeric(self, value: str) -> float:
        """Convierte un valor a numérico, retorna 0.0 si no es convertible"""
        try:
            if value and value.strip():
                return float(value)
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _convert_to_numeric_or_text(self, value: str, is_numeric: bool = False) -> Any:
        """Convierte un valor a numérico o lo mantiene como texto según el tipo"""
        if is_numeric:
            return self._convert_to_numeric(value)
        return value if value else ''
    
    def _build_concept_catalog(self, file_paths: List[str]):
        """Construye el catálogo unificado de conceptos de todos los archivos"""
        logger.info("🔍 Construyendo catálogo unificado de conceptos...")
        
        for file_path in file_paths:
            path = Path(file_path)
            
            if path.suffix.lower() == '.zip':
                self._extract_concepts_from_zip(str(path))
            elif path.suffix.lower() == '.xml':
                self._extract_concepts_from_xml(str(path))
        
        logger.info(f"📋 Catálogo construido: {len(self.conceptos_percepciones)} percepciones, {len(self.conceptos_deducciones)} deducciones, {len(self.conceptos_otros_pagos)} otros pagos")
    
    def _extract_concepts_from_zip(self, zip_path: str):
        """Extrae conceptos de un archivo ZIP para el catálogo"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                xml_files = [f for f in zip_file.namelist() if f.endswith('.xml')]
                
                for xml_file in xml_files:
                    try:
                        with zip_file.open(xml_file) as xml_content:
                            xml_data = xml_content.read()
                            self._extract_concepts_from_xml_content(xml_data)
                    except Exception as e:
                        logger.warning(f"⚠️ No se pudieron extraer conceptos de {xml_file}: {e}")
                        
        except Exception as e:
            logger.error(f"Error extrayendo conceptos del ZIP {zip_path}: {e}")
    
    def _extract_concepts_from_xml(self, xml_path: str):
        """Extrae conceptos de un archivo XML individual para el catálogo"""
        try:
            with open(xml_path, 'rb') as file:
                xml_data = file.read()
                self._extract_concepts_from_xml_content(xml_data)
        except Exception as e:
            logger.error(f"Error extrayendo conceptos del XML {xml_path}: {e}")
    
    def _extract_concepts_from_xml_content(self, xml_data: bytes):
        """Extrae conceptos del contenido XML para el catálogo"""
        try:
            root = ET.fromstring(xml_data)
            
            # Extraer conceptos de percepciones
            percepciones = root.findall('.//nomina12:Percepcion', self.namespaces)
            if not percepciones:
                percepciones = root.findall('.//Percepcion')
            
            for percepcion in percepciones:
                concepto = percepcion.get('Concepto', '')
                if concepto:
                    self.conceptos_percepciones.add(concepto)
            
            # Extraer conceptos de deducciones
            deducciones = root.findall('.//nomina12:Deduccion', self.namespaces)
            if not deducciones:
                deducciones = root.findall('.//Deduccion')
            
            for deduccion in deducciones:
                concepto = deduccion.get('Concepto', '')
                if concepto:
                    self.conceptos_deducciones.add(concepto)
            
            # Extraer conceptos de otros pagos
            otros_pagos = root.findall('.//nomina12:OtroPago', self.namespaces)
            if not otros_pagos:
                otros_pagos = root.findall('.//OtroPago')
            
            for otro_pago in otros_pagos:
                concepto = otro_pago.get('Concepto', '')
                if concepto:
                    self.conceptos_otros_pagos.add(concepto)
                    
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron extraer conceptos del contenido XML: {e}")
    
    def process_zip_file(self, zip_path: str) -> List[Dict[str, Any]]:
        """Procesa un archivo ZIP que contiene XMLs de nómina"""
        results = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                xml_files = [f for f in zip_file.namelist() if f.endswith('.xml')]
                
                logger.info(f"Procesando {len(xml_files)} archivos XML del ZIP")
                
                for xml_file in xml_files:
                    try:
                        with zip_file.open(xml_file) as xml_content:
                            xml_data = xml_content.read()
                            result = self.process_xml_content(xml_data, filename=xml_file)
                            if result:
                                results.append(result)
                                logger.info(f"✅ {xml_file} procesado exitosamente")
                            else:
                                logger.warning(f"⚠️ {xml_file} no pudo ser procesado")
                    except Exception as e:
                        logger.error(f"Error procesando {xml_file}: {e}")
                        
        except Exception as e:
            logger.error(f"Error abriendo ZIP {zip_path}: {e}")
            
        return results
    
    def process_xml_file(self, xml_path: str) -> Optional[Dict[str, Any]]:
        """Procesa un archivo XML individual"""
        try:
            with open(xml_path, 'rb') as file:
                xml_data = file.read()
                # Extraer solo el nombre del archivo sin la ruta
                filename = Path(xml_path).name
                return self.process_xml_content(xml_data, filename=filename)
        except Exception as e:
            logger.error(f"Error procesando XML {xml_path}: {e}")
            return None
    
    def process_xml_content(self, xml_data: bytes, filename: str = '') -> Optional[Dict[str, Any]]:
        """Procesa el contenido XML y extrae los datos de nómina"""
        try:
            # Intentar parsear el XML
            root = ET.fromstring(xml_data)
            
            # Buscar el comprobante con diferentes estrategias
            comprobante = None
            
            # Estrategia 1: Buscar con namespace específico
            comprobante = root.find('.//cfdi:Comprobante', self.namespaces)
            
            # Estrategia 2: Buscar sin namespace
            if comprobante is None:
                comprobante = root.find('.//Comprobante')
            
            # Estrategia 3: Buscar en el root si es el comprobante
            if comprobante is None and root.tag.endswith('Comprobante'):
                comprobante = root
            
            if not comprobante:
                logger.warning("No se encontró el elemento Comprobante")
                return None
                
            # Extraer datos del emisor (patrón)
            emisor_data = self._extract_emisor_data(root)
            
            # Extraer datos del receptor (trabajador)
            receptor_data = self._extract_receptor_data(root)
            
            # Extraer datos de nómina
            nomina_data = self._extract_nomina_data(root)
            
            # Extraer percepciones usando el catálogo unificado
            percepciones_data = self._extract_percepciones_data(root)
            
            # Extraer deducciones usando el catálogo unificado
            deducciones_data = self._extract_deducciones_data(root)
            
            # Extraer otros pagos usando el catálogo unificado
            otros_pagos_data = self._extract_otros_pagos_data(root)
            
            # Extraer UUID del CFDI
            uuid_data = self._extract_uuid_data(root, filename=filename)
            
            # Combinar todos los datos
            combined_data = {
                **emisor_data,
                **receptor_data,
                **nomina_data,
                **percepciones_data,
                **deducciones_data,
                **otros_pagos_data,
                **uuid_data
            }
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error procesando contenido XML: {e}")
            return None
    
    def _extract_emisor_data(self, root: ET.Element) -> Dict[str, Any]:
        """Extrae datos del emisor (patrón)"""
        data = {}
        
        # Buscar emisor con diferentes estrategias
        emisor = None
        nomina_emisor = None
        
        # Buscar emisor
        emisor = root.find('.//cfdi:Emisor', self.namespaces)
        if emisor is None:
            emisor = root.find('.//Emisor')
        
        # Buscar emisor de nómina
        nomina_emisor = root.find('.//nomina12:Emisor', self.namespaces)
        if nomina_emisor is None:
            nomina_emisor = root.find('.//Emisor')
        
        if emisor is not None:
            data.update({
                'Patron_RFC': emisor.get('Rfc', ''),
                'Patron_Nombre': emisor.get('Nombre', ''),
                'Patron_RegimenFiscal': emisor.get('RegimenFiscal', '')
            })
        
        if nomina_emisor is not None:
            data['Patron_RegistroPatronal'] = nomina_emisor.get('RegistroPatronal', '')
        
        return data
    
    def _extract_receptor_data(self, root: ET.Element) -> Dict[str, Any]:
        """Extrae datos del receptor (trabajador)"""
        data = {}
        
        # Buscar receptor con diferentes estrategias
        receptor = None
        nomina_receptor = None
        
        # Buscar receptor
        receptor = root.find('.//cfdi:Receptor', self.namespaces)
        if receptor is None:
            receptor = root.find('.//Receptor')
        
        # Buscar receptor de nómina
        nomina_receptor = root.find('.//nomina12:Receptor', self.namespaces)
        if nomina_receptor is None:
            nomina_receptor = root.find('.//Receptor')
        
        if receptor is not None:
            data.update({
                'Trabajador_RFC': receptor.get('Rfc', ''),
                'Trabajador_Nombre': receptor.get('Nombre', ''),
                'Trabajador_DomicilioFiscal': receptor.get('DomicilioFiscalReceptor', ''),
                'Trabajador_RegimenFiscal': receptor.get('RegimenFiscalReceptor', ''),
                'Trabajador_UsoCFDI': receptor.get('UsoCFDI', '')
            })
        
        if nomina_receptor is not None:
            data.update({
                'Trabajador_CURP': nomina_receptor.get('Curp', ''),
                'Trabajador_NSS': nomina_receptor.get('NumSeguridadSocial', ''),
                'Trabajador_FechaInicio': nomina_receptor.get('FechaInicioRelLaboral', ''),
                'Trabajador_Antiguedad': nomina_receptor.get('Antigüedad', ''),
                'Trabajador_TipoContrato': nomina_receptor.get('TipoContrato', ''),
                'Trabajador_Sindicalizado': nomina_receptor.get('Sindicalizado', ''),
                'Trabajador_TipoJornada': nomina_receptor.get('TipoJornada', ''),
                'Trabajador_TipoRegimen': nomina_receptor.get('TipoRegimen', ''),
                'Trabajador_NumEmpleado': nomina_receptor.get('NumEmpleado', ''),
                'Trabajador_Departamento': nomina_receptor.get('Departamento', ''),
                'Trabajador_Puesto': nomina_receptor.get('Puesto', ''),
                'Trabajador_RiesgoPuesto': nomina_receptor.get('RiesgoPuesto', ''),
                'Trabajador_PeriodicidadPago': nomina_receptor.get('PeriodicidadPago', ''),
                'Trabajador_SalarioBaseCotApor': self._convert_to_numeric(nomina_receptor.get('SalarioBaseCotApor', '0.00')),
                'Trabajador_SalarioDiarioIntegrado': self._convert_to_numeric(nomina_receptor.get('SalarioDiarioIntegrado', '0.00')),
                'Trabajador_ClaveEntFed': nomina_receptor.get('ClaveEntFed', '')
            })
        
        return data
    
    def _extract_nomina_data(self, root: ET.Element) -> Dict[str, Any]:
        """Extrae datos generales de la nómina"""
        data = {}
        
        # Buscar nómina con diferentes estrategias
        nomina = root.find('.//nomina12:Nomina', self.namespaces)
        if nomina is None:
            nomina = root.find('.//Nomina')
        
        if nomina is not None:
            data.update({
                'Nomina_Version': nomina.get('Version', ''),
                'Nomina_TipoNomina': nomina.get('TipoNomina', ''),
                'Nomina_FechaPago': nomina.get('FechaPago', ''),
                'Nomina_FechaInicialPago': nomina.get('FechaInicialPago', ''),
                'Nomina_FechaFinalPago': nomina.get('FechaFinalPago', ''),
                'Nomina_NumDiasPagados': self._convert_to_numeric(nomina.get('NumDiasPagados', '0.00')),
                'Nomina_TotalPercepciones': self._convert_to_numeric(nomina.get('TotalPercepciones', '0.00')),
                'Nomina_TotalDeducciones': self._convert_to_numeric(nomina.get('TotalDeducciones', '0.00')),
                'Nomina_TotalOtrosPagos': self._convert_to_numeric(nomina.get('TotalOtrosPagos', '0.00'))
            })
        
        return data
    
    def _extract_percepciones_data(self, root: ET.Element) -> Dict[str, Any]:
        """Extrae datos de percepciones usando el catálogo unificado"""
        data = {}
        
        # Crear un diccionario temporal con los valores encontrados
        percepciones_encontradas = {}
        
        # Buscar percepciones con diferentes estrategias
        percepciones = root.findall('.//nomina12:Percepcion', self.namespaces)
        if not percepciones:
            percepciones = root.findall('.//Percepcion')
        
        # Extraer valores de las percepciones encontradas
        for percepcion in percepciones:
            concepto = percepcion.get('Concepto', '')
            if concepto:
                percepciones_encontradas[concepto] = {
                    'ImporteGravado': self._convert_to_numeric(percepcion.get('ImporteGravado', '0.00')),
                    'ImporteExento': self._convert_to_numeric(percepcion.get('ImporteExento', '0.00')),
                    'Tipo': percepcion.get('TipoPercepcion', ''),
                    'Clave': percepcion.get('Clave', '')
                }
        
        # Crear columnas para TODOS los conceptos del catálogo, llenando con 0 si no existen
        for concepto in sorted(self.conceptos_percepciones):
            if concepto in percepciones_encontradas:
                # Concepto existe en este XML
                data[f'{concepto}_ImporteGravado'] = percepciones_encontradas[concepto]['ImporteGravado']
                data[f'{concepto}_ImporteExento'] = percepciones_encontradas[concepto]['ImporteExento']
                data[f'{concepto}_Tipo'] = percepciones_encontradas[concepto]['Tipo']
                data[f'{concepto}_Clave'] = percepciones_encontradas[concepto]['Clave']
            else:
                # Concepto no existe en este XML, llenar con valores por defecto
                data[f'{concepto}_ImporteGravado'] = 0.0
                data[f'{concepto}_ImporteExento'] = 0.0
                data[f'{concepto}_Tipo'] = ''
                data[f'{concepto}_Clave'] = ''
        
        return data
    
    def _extract_deducciones_data(self, root: ET.Element) -> Dict[str, Any]:
        """Extrae datos de deducciones usando el catálogo unificado"""
        data = {}
        
        # Crear un diccionario temporal con los valores encontrados
        deducciones_encontradas = {}
        
        # Buscar deducciones con diferentes estrategias
        deducciones = root.findall('.//nomina12:Deduccion', self.namespaces)
        if not deducciones:
            deducciones = root.findall('.//Deduccion')
        
        # Extraer valores de las deducciones encontradas
        for deduccion in deducciones:
            concepto = deduccion.get('Concepto', '')
            if concepto:
                deducciones_encontradas[concepto] = {
                    'Importe': self._convert_to_numeric(deduccion.get('Importe', '0.00')),
                    'Tipo': deduccion.get('TipoDeduccion', ''),
                    'Clave': deduccion.get('Clave', '')
                }
        
        # Crear columnas para TODOS los conceptos del catálogo, llenando con 0 si no existen
        for concepto in sorted(self.conceptos_deducciones):
            if concepto in deducciones_encontradas:
                # Concepto existe en este XML
                data[f'{concepto}_Importe'] = deducciones_encontradas[concepto]['Importe']
                data[f'{concepto}_Tipo'] = deducciones_encontradas[concepto]['Tipo']
                data[f'{concepto}_Clave'] = deducciones_encontradas[concepto]['Clave']
            else:
                # Concepto no existe en este XML, llenar con valores por defecto
                data[f'{concepto}_Importe'] = 0.0
                data[f'{concepto}_Tipo'] = ''
                data[f'{concepto}_Clave'] = ''
        
        return data
    
    def _extract_otros_pagos_data(self, root: ET.Element) -> Dict[str, Any]:
        """Extrae datos de otros pagos usando el catálogo unificado"""
        data = {}
        
        # Crear un diccionario temporal con los valores encontrados
        otros_pagos_encontrados = {}
        
        # Buscar otros pagos con diferentes estrategias
        otros_pagos = root.findall('.//nomina12:OtroPago', self.namespaces)
        if not otros_pagos:
            otros_pagos = root.findall('.//OtroPago')
        
        # Extraer valores de los otros pagos encontrados
        for otro_pago in otros_pagos:
            concepto = otro_pago.get('Concepto', '')
            if concepto:
                otros_pagos_encontrados[concepto] = {
                    'Importe': self._convert_to_numeric(otro_pago.get('Importe', '0.00')),
                    'Tipo': otro_pago.get('TipoOtroPago', ''),
                    'Clave': otro_pago.get('Clave', '')
                }
        
        # Crear columnas para TODOS los conceptos del catálogo, llenando con 0 si no existen
        for concepto in sorted(self.conceptos_otros_pagos):
            if concepto in otros_pagos_encontrados:
                # Concepto existe en este XML
                data[f'{concepto}_Importe'] = otros_pagos_encontrados[concepto]['Importe']
                data[f'{concepto}_Tipo'] = otros_pagos_encontrados[concepto]['Tipo']
                data[f'{concepto}_Clave'] = otros_pagos_encontrados[concepto]['Clave']
            else:
                # Concepto no existe en este XML, llenar con valores por defecto
                data[f'{concepto}_Importe'] = 0.0
                data[f'{concepto}_Tipo'] = ''
                data[f'{concepto}_Clave'] = ''
        
        return data
    
    def _extract_uuid_data(self, root: ET.Element, filename: str = '') -> Dict[str, Any]:
        """Extrae el UUID del CFDI desde múltiples ubicaciones posibles"""
        data = {}
        uuid = ''
        
        # Estrategia 1: Buscar en el elemento Comprobante (atributo UUID)
        comprobante = root.find('.//cfdi:Comprobante', self.namespaces)
        if comprobante is None:
            comprobante = root.find('.//Comprobante')
        
        if comprobante is not None:
            uuid = comprobante.get('UUID', '')
        
        # Estrategia 2: Buscar en el elemento TimbreFiscalDigital (atributo UUID)
        if not uuid:
            tfd = root.find('.//tfd:TimbreFiscalDigital', self.namespaces)
            if tfd is None:
                tfd = root.find('.//TimbreFiscalDigital')
            
            if tfd is not None:
                uuid = tfd.get('UUID', '')
        
        # Estrategia 3: Buscar en el root si es el comprobante
        if not uuid and root.tag.endswith('Comprobante'):
            uuid = root.get('UUID', '')
        
        # Estrategia 4: Buscar en cualquier elemento con atributo UUID
        if not uuid:
            uuid_elements = root.findall('.//*[@UUID]')
            if uuid_elements:
                uuid = uuid_elements[0].get('UUID', '')
        
        # Estrategia 5: Extraer UUID del nombre del archivo (formato: UUID.xml)
        if not uuid and filename:
            # Buscar patrón UUID en el nombre del archivo
            uuid_pattern = r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})'
            match = re.search(uuid_pattern, filename, re.IGNORECASE)
            if match:
                uuid = match.group(1)
                logger.info(f"✅ UUID extraído del nombre del archivo: {uuid}")
        
        data['CFDI_UUID'] = uuid if uuid else ''
        
        if uuid:
            logger.info(f"✅ UUID encontrado: {uuid}")
        else:
            logger.warning("⚠️ No se encontró UUID en el XML ni en el nombre del archivo")
        
        return data
    
    def process_multiple_files(self, file_paths: List[str]) -> pd.DataFrame:
        """Procesa múltiples archivos y retorna un DataFrame consolidado"""
        # PASO 1: Construir catálogo unificado de conceptos
        self._build_concept_catalog(file_paths)
        
        # PASO 2: Procesar archivos con el catálogo establecido
        all_results = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            if path.suffix.lower() == '.zip':
                results = self.process_zip_file(str(path))
                all_results.extend(results)
            elif path.suffix.lower() == '.xml':
                result = self.process_xml_file(str(path))
                if result:
                    all_results.append(result)
        
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Convertir columnas de importes a numérico
            df = self._convert_import_columns_to_numeric(df)
            
            return df
        else:
            return pd.DataFrame()
    
    def _convert_import_columns_to_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convierte automáticamente las columnas de importes a numérico"""
        for column in df.columns:
            # Identificar columnas de importes por su nombre
            if any(keyword in column.lower() for keyword in ['importe', 'salario', 'total', 'deduccion', 'percepcion']):
                try:
                    # Convertir a numérico, llenando valores no numéricos con 0
                    df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0.0)
                    logger.info(f"✅ Columna '{column}' convertida a numérico")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo convertir columna '{column}' a numérico: {e}")
        
        return df
    
    def export_to_excel(self, df: pd.DataFrame, output_path: str = None) -> bytes:
        """Exporta el DataFrame a Excel y retorna los bytes del archivo"""
        if output_path is None:
            output_path = 'nomina_consolidada.xlsx'
        
        # Crear un writer de Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
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
        
        # Leer el archivo generado y retornar bytes
        with open(output_path, 'rb') as f:
            excel_bytes = f.read()
        
        return excel_bytes
