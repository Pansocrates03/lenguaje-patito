from grammar import CICLO, ESTATUTO, CUERPO

print("Test 1: Parsear CICLO directamente")
ciclo_code = """mientras (x < 10) {
    x = x + 1;
};"""

try:
    result = CICLO.parse_string(ciclo_code)
    print(f"CICLO parseado correctamente: {result}")
except Exception as e:
    print(f"Error al parsear CICLO: {e}")

print("\nTest 2: Parsear CICLO como ESTATUTO")
try:
    result = ESTATUTO.parse_string(ciclo_code)
    print(f"ESTATUTO (ciclo) parseado: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest 3: Parsear CUERPO con ciclo")
cuerpo_code = """{
    mientras (x < 10) {
        x = x + 1;
    };
}"""

try:
    result = CUERPO.parse_string(cuerpo_code)
    print(f"CUERPO parseado: {result}")
except Exception as e:
    print(f"Error: {e}")
