from grammar import IMPRIME, ESTATUTO, CUERPO

print("Test 1: Parsear IMPRIME directamente")
imprime_code = "escribe (sum(1, 2 + 3));"

try:
    result = IMPRIME.parse_string(imprime_code)
    print(f"IMPRIME parseado correctamente: {result}")
except Exception as e:
    print(f"Error al parsear IMPRIME: {e}")

print("\nTest 2: Parsear IMPRIME como ESTATUTO")
try:
    result = ESTATUTO.parse_string(imprime_code)
    print(f"ESTATUTO (imprime) parseado: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest 3: Parsear CUERPO con imprime")
cuerpo_code = """{
    escribe (sum(1, 2 + 3));
}"""

try:
    result = CUERPO.parse_string(cuerpo_code)
    print(f"CUERPO parseado: {result}")
except Exception as e:
    print(f"Error: {e}")
