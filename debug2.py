from grammar import TIPO, IDENTIFICADOR, CUERPO, ESTATUTO, ASIGNA, EXPRESION

# Test step by step
print("Test 1: Parsear TIPO")
try:
    print(TIPO.parse_string("entero"))
except Exception as e:
    print(f"Error: {e}")

print("\nTest 2: Parsear IDENTIFICADOR")
try:
    print(IDENTIFICADOR.parse_string("suma"))
except Exception as e:
    print(f"Error: {e}")

print("\nTest 3: Parsear ASIGNA")
try:
    result = ASIGNA.parse_string("resultado = a + b;")
    print(f"ASIGNA parseado: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest 4: Parsear CUERPO")
try:
    body = """{
    resultado = a + b;
}"""
    result = CUERPO.parse_string(body)
    print(f"CUERPO parseado: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest 5: Parsear función completa sin la última llave")
test_func = """entero suma(a: entero, b: entero)
{
    {
        resultado = a + b;
    }
}"""
print(f"Función:\n{test_func}")
