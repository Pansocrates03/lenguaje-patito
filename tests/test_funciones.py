import pytest
from grammar import crear_gramática
from semantic_context import SemanticContext

def compilar_y_obtener_cuadruplos(codigo: str) -> list:
    semantic = SemanticContext()
    lenguaje_patito = crear_gramática(semantic)
    lenguaje_patito.parse_string(codigo)
    return semantic.obtener_cuadruplos()

# 1. Separamos los casos en una variable
CASOS_PRUEBA = [
    (
        "Programa sin funciones (Salto basico)",
        """
        programa test_main_solo;
        inicio {
            escribe(1);
        } fin
        """,
        [
            ("GOTO", "_", "_", 1),
            ("PRINT", "1", "_", "_")
        ]
    ),
    # ... (AQUÍ VAN TODOS TUS DEMÁS CASOS EXACTAMENTE IGUAL) ...
    (
        "Llamada a funcion con retorno en expresion",
        """
        programa test_call_return;
        vars x: entero;
        
        entero multiplica(a: entero) {
            {
                escribe(a);
            }
        };
        
        inicio {
            x = multiplica(5) + 2;
        } fin
        """,
        [
            ("GOTO", "_", "_", 3),
            ("PRINT", "a", "_", "_"),
            ("ENDFUNC", "_", "_", "_"),
            ("ERA", "multiplica", "_", "_"),
            ("PARAM", "5", "_", "param0"),
            ("GOSUB", "multiplica", "_", 1),
            ("=", "multiplica", "_", "t1"),
            ("+", "t1", "2", "t2"),
            ("=", "t2", "_", "x")
        ]
    )
]

# 2. Pasamos la lista y usamos 'ids' para que la terminal solo muestre el nombre del caso
@pytest.mark.parametrize("nombre_prueba, codigo, expected_ops", CASOS_PRUEBA, ids=[caso[0] for caso in CASOS_PRUEBA])
def test_generacion_cuadruplos_funciones(nombre_prueba, codigo, expected_ops):
    
    # 3. Bloque try-except para atrapar el error e imprimir bonito
    try:
        cuadruplos = compilar_y_obtener_cuadruplos(codigo)
    except Exception as e:
        print(f"\n\n{'='*60}")
        print(f"💥 ERROR DURANTE LA COMPILACIÓN: {nombre_prueba}")
        print(f"{'='*60}")
        print("CÓDIGO FUENTE EVALUADO:")
        print(codigo) # Aquí se imprime respetando espacios y saltos de línea
        print(f"{'='*60}\n")
        
        # Hacemos que la prueba falle limpiamente con el mensaje de error de tu compilador
        pytest.fail(f"Excepción del compilador: {str(e)}")

    # Assert - Verificamos cantidad
    assert len(cuadruplos) == len(expected_ops), f"Fallo en {nombre_prueba}: Se esperaban {len(expected_ops)} cuádruplos, se obtuvieron {len(cuadruplos)}."
    
    # Assert - Verificamos cada instrucción
    for i, (cuadruplo, (exp_op, exp_op1, exp_op2, exp_res)) in enumerate(zip(cuadruplos, expected_ops)):
        assert cuadruplo.operador == exp_op, f"[{i}] Operador incorrecto: esperado '{exp_op}', obtenido '{cuadruplo.operador}'"
        assert str(cuadruplo.operando1) == exp_op1, f"[{i}] Operando 1 incorrecto: esperado '{exp_op1}', obtenido '{cuadruplo.operando1}'"
        assert str(cuadruplo.operando2) == exp_op2, f"[{i}] Operando 2 incorrecto: esperado '{exp_op2}', obtenido '{cuadruplo.operando2}'"
        assert cuadruplo.resultado == exp_res, f"[{i}] Resultado incorrecto: esperado '{exp_res}', obtenido '{cuadruplo.resultado}'"