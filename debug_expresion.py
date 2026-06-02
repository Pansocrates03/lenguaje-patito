from grammar import EXPRESION, FACTOR, LLAMADA

print("Test 1: Parsear LLAMADA")
try:
    result = LLAMADA.parse_string("sum(1, 2 + 3)")
    print(f"LLAMADA parseado: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest 2: Parsear como FACTOR")
try:
    result = FACTOR.parse_string("sum(1, 2 + 3)")
    print(f"FACTOR parseado: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest 3: Parsear como EXPRESION")
try:
    result = EXPRESION.parse_string("sum(1, 2 + 3)")
    print(f"EXPRESION parseado: {result}")
except Exception as e:
    print(f"Error: {e}")
