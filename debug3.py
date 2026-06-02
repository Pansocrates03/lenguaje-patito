from grammar import CUERPO, ESTATUTO, ASIGNA

print("Test: Parsear dos asignaciones en CUERPO")
code = """{
    x = 10;
    y = 3.14;
}"""

print(f"Código:\n{code}\n")

try:
    result = CUERPO.parse_string(code)
    print(f"CUERPO parseado: {result}")
    print(f"Elementos: {list(result)}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest: Parsear una sola asignación")
code2 = "{x = 10;}"
try:
    result = CUERPO.parse_string(code2)
    print(f"CUERPO parseado: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest: Parsear ESTATUTO directamente")
try:
    result = ESTATUTO.parse_string("x = 10;")
    print(f"ESTATUTO 'x = 10;' parseado: {result}")
    result = ESTATUTO.parse_string("y = 3.14;")
    print(f"ESTATUTO 'y = 3.14;' parseado: {result}")
except Exception as e:
    print(f"Error: {e}")
