import xml.etree.ElementTree as ET
import pandas as pd
import io
from typing import Dict, Any, List, Optional
import logging
import re
import os
import zipfile
from io import BytesIO

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NominaXMLHandler:
    def __init__(self):
        self.namespaces = {
            'cfdi3': 'http://www.sat.gob.mx/cfd/3',
            'cfdi4': 'http://www.sat.gob.mx/cfd/4',
            'nomina12': 'http://www.sat.gob.mx/nomina12',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }
        # Metadata to track column sorting info: name -> (SectionPriority, ClaveInt, SubitemPriority)
        # SectionPriority: 0=Standard, 1=Percepciones, 2=Deducciones, 3=OtrosPagos
        self.column_metadata = {}

    def _get_attr(self, element: ET.Element, name: str, default: str = '') -> str:
        """Get attribute case-insensitive."""
        if element is None:
            return default
        val = element.get(name)
        if val is not None:
            return val
        name_lower = name.lower()
        for k, v in element.attrib.items():
            if k.lower() == name_lower:
                return v
        return default

    def _to_float(self, val: str) -> float:
        try:
            return float(val) if val else 0.0
        except ValueError:
            return 0.0
            
    def _register_metadata(self, col_name: str, section: str, clave: str, subitem_priority: int = 0):
        """
        Register metadata for sorting.
        Section: 'Standard', 'Percepciones', 'Deducciones', 'OtrosPagos'
        Clave: The numeric string code (e.g. "001")
        SubitemPriority: For ordering Gravado (0) vs Exento (1) or others.
        """
        priority_map = {
            'Standard': 0,
            'Percepciones': 1,
            'Deducciones': 2,
            'OtrosPagos': 3,
            'Totals': 4
        }
        
        try:
            clave_int = int(clave)
        except (ValueError, TypeError):
            clave_int = 99999 # Fallback for non-numeric keys
            
        self.column_metadata[col_name] = (priority_map.get(section, 99), clave_int, subitem_priority, col_name)

    def parse_xml_content(self, xml_content: bytes, filename: str) -> Dict[str, Any]:
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            logger.error(f"Error parsing XML: {filename}")
            return {}

        ns = dict(self.namespaces)
        data = {'NombreArchivo': filename}
        self._register_metadata('NombreArchivo', 'Standard', '0')

        def find_path(node, path):
            for prefix in ['cfdi4', 'cfdi3']:
                res = node.find(f'{{{self.namespaces[prefix]}}}{path}')
                if res is not None: return res
            return node.find(path)

        # 1. Attributes of Comprobante
        comprobante = root
        if not root.tag.endswith('Comprobante'):
            found = find_path(root, 'Comprobante')
            if found is not None:
                comprobante = found

        for attr in ['Serie', 'Folio', 'Fecha', 'Moneda', 'Sello']:
            data[attr] = self._get_attr(comprobante, attr)
            self._register_metadata(attr, 'Standard', '0')
            
        for attr in ['Total', 'SubTotal']:
            data[attr] = self._to_float(self._get_attr(comprobante, attr))
            self._register_metadata(attr, 'Standard', '99') # Totals usually at end, but user wants Percepciones->Deducciones->OtrosPagos. 
            # If we want Total AFTER others, we need higher priority.
            # Let's put Total and Subtotal at Priority 4 (After OtrosPagos=3)
            self._register_metadata(attr, 'Totals', '0')

        # 2. Emisor / Receptor
        emisor = find_path(comprobante, 'Emisor')
        if emisor is not None:
            data['Emisor_RFC'] = self._get_attr(emisor, 'Rfc')
            data['Emisor_Nombre'] = self._get_attr(emisor, 'Nombre')
            data['Emisor_RegimenFiscal'] = self._get_attr(emisor, 'RegimenFiscal')
            for k in ['Emisor_RFC', 'Emisor_Nombre', 'Emisor_RegimenFiscal']:
                self._register_metadata(k, 'Standard', '1')

        receptor = find_path(comprobante, 'Receptor')
        if receptor is not None:
            data['Receptor_RFC'] = self._get_attr(receptor, 'Rfc')
            data['Receptor_Nombre'] = self._get_attr(receptor, 'Nombre')
            data['Receptor_UsoCFDI'] = self._get_attr(receptor, 'UsoCFDI')
            for k in ['Receptor_RFC', 'Receptor_Nombre', 'Receptor_UsoCFDI']:
                self._register_metadata(k, 'Standard', '2')

        # 3. UUID
        complemento = find_path(comprobante, 'Complemento')
        if complemento is not None:
            tfd = complemento.find(f'{{{self.namespaces["tfd"]}}}TimbreFiscalDigital')
            if tfd is not None:
                data['UUID'] = self._get_attr(tfd, 'UUID')
                data['FechaTimbrado'] = self._get_attr(tfd, 'FechaTimbrado')
                self._register_metadata('UUID', 'Standard', '0')
                self._register_metadata('FechaTimbrado', 'Standard', '0')

        # 4. Nomina
        nomina = None
        if complemento is not None:
            nomina = complemento.find(f'{{{self.namespaces["nomina12"]}}}Nomina')
        
        if nomina is not None:
            # Nomina Headers
            for attr in ['FechaPago', 'FechaInicialPago', 'FechaFinalPago']:
                 data[attr] = self._get_attr(nomina, attr)
                 self._register_metadata(attr, 'Standard', '3')
            
            # NumDiasPagados stays standard
            data['NumDiasPagados'] = self._to_float(self._get_attr(nomina, 'NumDiasPagados'))
            self._register_metadata('NumDiasPagados', 'Standard', '4')

            # Move Totals to their respective sections
            # We use 'Total' as clave which defaults to 99999 (End of section)
            
            tp = self._to_float(self._get_attr(nomina, 'TotalPercepciones'))
            data['TotalPercepciones'] = tp
            self._register_metadata('TotalPercepciones', 'Percepciones', 'Total')
            
            td = self._to_float(self._get_attr(nomina, 'TotalDeducciones'))
            data['TotalDeducciones'] = td
            self._register_metadata('TotalDeducciones', 'Deducciones', 'Total')
            
            top = self._to_float(self._get_attr(nomina, 'TotalOtrosPagos'))
            data['TotalOtrosPagos'] = top
            self._register_metadata('TotalOtrosPagos', 'OtrosPagos', 'Total')

            ns_nomina = {'n': self.namespaces['nomina12']}
            
            # A. Percepciones
            percepciones_node = nomina.find('n:Percepciones', ns_nomina)
            if percepciones_node is not None:
                for p in percepciones_node.findall('n:Percepcion', ns_nomina):
                    clave = self._get_attr(p, 'Clave') or self._get_attr(p, 'TipoPercepcion')
                    concepto = self._get_attr(p, 'Concepto')
                    gravado = self._get_attr(p, 'ImporteGravado')
                    exento = self._get_attr(p, 'ImporteExento')
                    
                    if concepto:
                        col_g = f'{concepto}_Gravado'
                        col_e = f'{concepto}_Exento'
                        data[col_g] = self._to_float(gravado)
                        data[col_e] = self._to_float(exento)
                        
                        self._register_metadata(col_g, 'Percepciones', clave, 0)
                        self._register_metadata(col_e, 'Percepciones', clave, 1)

            # B. Deducciones
            deducciones_node = nomina.find('n:Deducciones', ns_nomina)
            if deducciones_node is not None:
                for d in deducciones_node.findall('n:Deduccion', ns_nomina):
                    clave = self._get_attr(d, 'Clave') or self._get_attr(d, 'TipoDeduccion')
                    concepto = self._get_attr(d, 'Concepto')
                    importe = self._get_attr(d, 'Importe')
                    
                    if concepto:
                        data[concepto] = self._to_float(importe)
                        self._register_metadata(concepto, 'Deducciones', clave, 0)

            # C. Otros Pagos
            otros_pagos_node = nomina.find('n:OtrosPagos', ns_nomina)
            if otros_pagos_node is not None:
                for o in otros_pagos_node.findall('n:OtroPago', ns_nomina):
                    clave = self._get_attr(o, 'Clave') or self._get_attr(d, 'TipoOtroPago')
                    concepto = self._get_attr(o, 'Concepto')
                    importe = self._get_attr(o, 'Importe')
                    
                    if concepto:
                        data[concepto] = self._to_float(importe)
                        self._register_metadata(concepto, 'OtrosPagos', clave, 0)
                        
                        subsidio = o.find('n:SubsidioAlEmpleo', ns_nomina)
                        if subsidio is not None:
                            sub_causado = self._get_attr(subsidio, 'SubsidioCausado')
                            if sub_causado:
                                col_sub = 'SubsidioCausado'
                                data[col_sub] = self._to_float(sub_causado)
                                self._register_metadata(col_sub, 'OtrosPagos', clave, 1) 

        return data

    def scan_directory(self, path: str) -> List[Any]:
        """
        Recursively scans a directory for .xml and .zip files.
        Returns a list of file-like objects (BytesIO) or tuples (content, filename).
        """
        found_files = []
        
        if not os.path.exists(path):
            return []

        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                if file.lower().endswith('.xml'):
                    try:
                        with open(full_path, 'rb') as f:
                            content = f.read()
                        found_files.append((content, file))
                    except Exception as e:
                        logger.error(f"Error reading {full_path}: {e}")
                
                elif file.lower().endswith('.zip'):
                    found_files.extend(self._process_zip(full_path))
                    
        return found_files

    def _process_zip(self, zip_path: str) -> List[Any]:
        results = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for filename in z.namelist():
                    if filename.lower().endswith('.xml'):
                        try:
                            content = z.read(filename)
                            # Use basename for simplicity in reports
                            name = os.path.basename(filename) 
                            results.append((content, name))
                        except Exception as e:
                            logger.error(f"Error reading {filename} in zip {zip_path}: {e}")
        except Exception as e:
            logger.error(f"Error processing zip {zip_path}: {e}")
        return results

    def process_files(self, files: List[Any]) -> pd.DataFrame:
        all_data = []
        
        for item in files:
            content = None
            name = "unknown"
            
            # Case 1: Streamlit UploadedFile
            if hasattr(item, 'read') and hasattr(item, 'name'):
                content = item.read()
                name = item.name
                item.seek(0)
            
            # Case 2: Tuple (content_bytes, filename) from scan_directory
            elif isinstance(item, tuple) and len(item) == 2:
                content = item[0]
                name = item[1]
                
            # Case 3: Path string (legacy support)
            elif isinstance(item, str) and os.path.exists(item):
                with open(item, 'rb') as f:
                    content = f.read()
                name = os.path.basename(item)

            if content:
                parsed = self.parse_xml_content(content, name)
                if parsed:
                    all_data.append(parsed)
        
        if not all_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(all_data)
        
        # SORTING LOGIC
        # Get all present columns
        cols = list(df.columns)
        
        # Define a sorting key function
        # Defaults for unknown columns: Standard, High int key, 0
        def sort_key(col_name):
            meta = self.column_metadata.get(col_name, (0, 99999, 0, col_name))
            return meta

        cols.sort(key=sort_key)
        
        # Reorder DataFrame
        df = df[cols]
        
        # Fill NaNs
        # Heuristic: If it's a numeric column (float), fill with 0.0
        # Check dtypes
        for col in df.columns:
            if pd.api.types.is_float_dtype(df[col]):
                 df[col] = df[col].fillna(0.0)
            elif pd.api.types.is_integer_dtype(df[col]):
                 df[col] = df[col].fillna(0)
        
        return df
