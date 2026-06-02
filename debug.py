from grammar import FUNCS, lenguaje_patito

# Prueba simple de FUNCS
test_func = """entero suma(a: entero, b: entero)
{
    {
        x = 1;
    }
}"""

print("Intentando parsear función:")
print(test_func)
print("\n---\n")

try:
    result = FUNCS.parse_string(test_func)
    print("Función parseada correctamente:")
    print(result)
except Exception as e:
    print(f"Error al parsear función: {e}")

print("\n\n---\n")

# Ahora prueba el programa completo
full_program = """programa mi_programa;

vars
    x: entero;
    y: flotante;

entero suma(a: entero, b: entero)
{
    {
        resultado = a + b;
    }
}

inicio
{
    x = 10;
    y = 3.14;
}
fin"""

print("Intentando parsear programa completo:")
try:
    result = lenguaje_patito.parse_string(full_program)
    print("Programa parseado correctamente!")
except Exception as e:
    print(f"Error: {e}")
