import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'V3'))

from xml_handler import NominaXMLHandler
import pandas as pd

def test_sorting():
    handler = NominaXMLHandler()
    
    # Simulate metadata registration from parsing multiple files
    # Standard
    handler._register_metadata('NombreArchivo', 'Standard', '0')
    handler._register_metadata('UUID', 'Standard', '0')
    handler._register_metadata('Total', 'Totals', '0')
    
    # Percepciones
    # "001" Sueldo, "038" Otros
    handler._register_metadata('Sueldo_Gravado', 'Percepciones', '001', 0)
    handler._register_metadata('Sueldo_Exento', 'Percepciones', '001', 1)
    handler._register_metadata('Bono_Gravado', 'Percepciones', '038', 0)
    handler._register_metadata('TotalPercepciones', 'Percepciones', 'Total')
    
    # Deducciones
    # "001" ISR, "002" IMSS
    handler._register_metadata('ISR', 'Deducciones', '001', 0)
    handler._register_metadata('IMSS', 'Deducciones', '002', 0)
    handler._register_metadata('TotalDeducciones', 'Deducciones', 'Total')
    
    # Otros Pagos
    # "002" Subsidio
    handler._register_metadata('Subsidio', 'OtrosPagos', '002', 0)
    handler._register_metadata('TotalOtrosPagos', 'OtrosPagos', 'Total')
    
    # Create a dummy DF with these columns in random order
    data = {
        'IMSS': [1],
        'Sueldo_Exento': [1],
        'TotalDeducciones': [1],
        'Total': [100],
        'Subsidio': [1],
        'NombreArchivo': ['file.xml'],
        'Bono_Gravado': [1],
        'TotalOtrosPagos': [1],
        'ISR': [1],
        'TotalPercepciones': [1],
        'UUID': ['abc-123'],
        'Sueldo_Gravado': [1]
    }
    
    # Manually invoke the sort logic by creating a dummy DF and using the handler's metadata
    df = pd.DataFrame(data)
    
    cols = list(df.columns)
    
    def sort_key(col_name):
        # Using default if not found, but we registered them all
        meta = handler.column_metadata.get(col_name, (0, 99999, 0, col_name))
        return meta
        
    cols.sort(key=sort_key)
    
    print("Sorted Columns:")
    print(cols)
    
    # Expected Order:
    # 1. Standard (NombreArchivo, UUID)
    # 2. Percepciones 001 (Sueldo_Gravado, Sueldo_Exento)
    # 3. Percepciones 038 (Bono_Gravado)
    # 4. Deducciones 001 (ISR)
    # 5. Deducciones 002 (IMSS)
    # 6. OtrosPagos 002 (Subsidio)
    # 7. Standard 99 (Total)
    
    # Note: 'UUID' and 'NombreArchivo' both have priority 0, clave 0.
    # Secondary sort implicit (insertion order? or unstable?).
    # Actually tuple comparison: (0, 0, 0, 'NombreArchivo') vs (0, 0, 0, 'UUID').
    # It will sort alphabetically by col_name as the last element of the tuple!
    
    expected_order = [
         'NombreArchivo', 'UUID', # Both Priority 0, Clave 0. Check name sort.
         'Sueldo_Gravado', 'Sueldo_Exento',
         'Bono_Gravado',
         'ISR',
         'IMSS',
         'Subsidio',
         'Total'
    ]
    
    # Let's see what we actually get, but 'NombreArchivo' < 'UUID' so that holds.
    # 'Sueldo_Gravado' (Subitem 0) vs 'Sueldo_Exento' (Subitem 1).
    
    failed = False
    for i, col in enumerate(cols):
        if i < len(expected_order):
            # Check relative orderting logic mainly
            pass
            
    # Check specific relative orders
    def check_before(a, b):
        if a in cols and b in cols:
            idx_a = cols.index(a)
            idx_b = cols.index(b)
            if idx_a < idx_b:
                print(f"PASS: {a} is before {b}")
            else:
                print(f"FAIL: {a} is NOT before {b}")
                return False
        return True

    results = [
        check_before('NombreArchivo', 'Sueldo_Gravado'), # Std vs Perc
        check_before('Sueldo_Gravado', 'ISR'), # Perc vs Ded
        check_before('ISR', 'Subsidio'), # Ded vs OP
        check_before('Subsidio', 'Total'), # OP vs StdEnd
        check_before('Sueldo_Gravado', 'Sueldo_Exento'), # Subitem sort
        
        # Section Grouping Checks
        check_before('Bono_Gravado', 'TotalPercepciones'), # Perc Item vs Perc Total
        check_before('TotalPercepciones', 'ISR'), # Perc Total vs Ded Item
        check_before('IMSS', 'TotalDeducciones'), # Ded Item vs Ded Total
        check_before('TotalDeducciones', 'Subsidio'), # Ded Total vs OP Item
        check_before('Subsidio', 'TotalOtrosPagos'), # OP Item vs OP Total
        check_before('TotalOtrosPagos', 'Total'), # OP Total vs Final Total
    ]
    
    if all(results):
        print("\nALL CHECKS PASSED")
    else:
        print("\nSOME CHECKS FAILED")

if __name__ == "__main__":
    test_sorting()
