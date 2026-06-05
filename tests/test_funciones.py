import pytest
from grammar import crear_gramática
from semantic_context import SemanticContext

# Helper para compilar código en crudo y extraer los cuádruplos generados
def compilar_y_obtener_cuadruplos(codigo: str) -> list:
    semantic = SemanticContext()
    lenguaje_patito = crear_gramática(semantic)
    lenguaje_patito.parseString(codigo)
    return semantic.obtener_cuadruplos()

@pytest.mark.parametrize("nombre_prueba, codigo, expected_ops", [
    (
        "Programa sin funciones (Salto basico)",
        """
        programa test_main_solo;
        inicio {
            escribe(1);
        } fin
        """,
        [
            # 0: GOTO inicial generado por action_programa_inicio
            # Brinca directamente a la primera instrucción del inicio (1)
            ("GOTO", "_", "_", 1),
            
            # 1: Cuerpo del inicio
            ("PRINT", "1", "_", "_")
        ]
    ),
    (
        "Programa con una funcion simple",
        """
        programa test_func_simple;
        
        nula mi_func() {
            {
                escribe(2);
            }
        };
        
        inicio {
            escribe(1);
        } fin
        """,
        [
            # 0: GOTO inicial. Ahora debe saltarse la función y brincar al cuádruplo 3
            ("GOTO", "_", "_", 3),
            
            # 1: Instrucciones dentro de la función
            ("PRINT", "2", "_", "_"),
            
            # 2: Finalización de la función (generada por action_funcion_end)
            ("ENDFUNC", "_", "_", "_"),
            
            # 3: Inicio del programa principal
            ("PRINT", "1", "_", "_")
        ]
    ),
    (
        "Programa con funciones, parametros y variables locales",
        """
        programa test_func_completa;
        
        entero suma(a: entero, b: entero) {
            vars
                res: entero;
            {
                res = a + b;
            }
        };
        
        inicio {
            escribe(1);
        } fin
        """,
        [
            # 0: GOTO inicial brinca todo el bloque de 'suma', cayendo en el índice 4
            ("GOTO", "_", "_", 4),
            
            # --- Inicia cuádruplos de la función 'suma' ---
            
            # 1: Evaluación de la expresión aritmética local
            ("+", "a", "b", "t1"),
            
            # 2: Asignación a la variable local 'res'
            ("=", "t1", "_", "res"),
            
            # 3: Finalización de la función
            ("ENDFUNC", "_", "_", "_"),
            
            # --- Inicia el main ---
            
            # 4: Instrucción del bloque principal
            ("PRINT", "1", "_", "_")
        ]
    )
])
def test_generacion_cuadruplos_funciones(nombre_prueba, codigo, expected_ops):
    # Act
    cuadruplos = compilar_y_obtener_cuadruplos(codigo)
    
    # Assert - Verificamos cantidad (Todo en una sola línea para evitar errores de sintaxis)
    assert len(cuadruplos) == len(expected_ops), f"Fallo en {nombre_prueba}: Se esperaban {len(expected_ops)} cuádruplos, se obtuvieron {len(cuadruplos)}."
    
    # Assert - Verificamos cada instrucción
    for i, (cuadruplo, (exp_op, exp_op1, exp_op2, exp_res)) in enumerate(zip(cuadruplos, expected_ops)):
        assert cuadruplo.operador == exp_op, f"[{i}] Operador incorrecto: esperado '{exp_op}', obtenido '{cuadruplo.operador}'"
        assert str(cuadruplo.operando1) == exp_op1, f"[{i}] Operando 1 incorrecto: esperado '{exp_op1}', obtenido '{cuadruplo.operando1}'"
        assert str(cuadruplo.operando2) == exp_op2, f"[{i}] Operando 2 incorrecto: esperado '{exp_op2}', obtenido '{cuadruplo.operando2}'"
        assert cuadruplo.resultado == exp_res, f"[{i}] Resultado incorrecto: esperado '{exp_res}', obtenido '{cuadruplo.resultado}'"