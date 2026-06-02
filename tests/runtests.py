
import os
import sys
from pathlib import Path

# Agregar la raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import Compilador

fixture_path = Path(__file__).parent / "fixtures"

def run_tests():
    compilador = Compilador()
    fixtures = sorted([f for f in fixture_path.glob("*.patito")])
    
    passed = 0
    failed = 0
    errors = []
    
    print("=" * 70)
    print("TEST SUITE - Lenguaje Patito")
    print("=" * 70)
    print()
    
    for fixture in fixtures:
        filename = fixture.name
        should_pass = "invalid" not in filename
        
        try:
            with open(fixture, 'r') as f:
                content = f.read()
            
            # Intentar parsear
            from grammar import lenguaje_patito
            try:
                lenguaje_patito.parse_string(content)
                parse_success = True
                error_msg = None
            except Exception as e:
                parse_success = False
                error_msg = str(e)
            
            # Verificar si el resultado es el esperado
            if should_pass:
                if parse_success:
                    print(f"✓ PASS: {filename}")
                    passed += 1
                else:
                    print(f"✗ FAIL: {filename}")
                    print(f"  Esperado: pasar")
                    print(f"  Error: {error_msg}")
                    print()
                    failed += 1
                    errors.append((filename, error_msg))
            else:
                if not parse_success:
                    print(f"✓ PASS: {filename} (falló como se esperaba)")
                    passed += 1
                else:
                    print(f"✗ FAIL: {filename}")
                    print(f"  Esperado: fallar")
                    print(f"  Resultado: parseó correctamente (debería haber fallado)")
                    print()
                    failed += 1
                    errors.append((filename, "No falló como se esperaba"))
                    
        except Exception as e:
            print(f"✗ ERROR: {filename}")
            print(f"  {str(e)}")
            print()
            failed += 1
            errors.append((filename, str(e)))
    
    print()
    print("=" * 70)
    print(f"RESULTADOS: {passed} pasaron, {failed} fallaron")
    print("=" * 70)
    
    if errors:
        print("\nDETALLE DE FALLOS:")
        for filename, error in errors:
            print(f"\n{filename}:")
            print(f"  {error}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)