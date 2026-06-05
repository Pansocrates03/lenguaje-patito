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
    ),
    (
        "Llamada a funcion sin parametros (Nula)",
        """
        programa test_call_simple;
        
        nula saludo() {
            {
                escribe(1);
            }
        };
        
        inicio {
            saludo();
        } fin
        """,
        [
            # 0: Salto inicial
            ("GOTO", "_", "_", 3),
            
            # --- Declaración de 'saludo' ---
            # 1: Cuerpo
            ("PRINT", "1", "_", "_"),
            # 2: Fin de función
            ("ENDFUNC", "_", "_", "_"),
            
            # --- Ejecución del inicio ---
            # 3: ERA (Reserva de memoria)
            ("ERA", "saludo", "_", "_"),
            
            # 4: GOSUB (Salto a la primera instrucción de la función, índice 1)
            ("GOSUB", "saludo", "_", 1)
        ]
    ),
    (
        "Llamada a funcion con parametros",
        """
        programa test_call_params;
        
        nula suma(a: entero, b: entero) {
            {
                escribe(a + b);
            }
        };
        
        inicio {
            suma(5, 10);
        } fin
        """,
        [
            # 0: Salto inicial
            ("GOTO", "_", "_", 4),
            
            # --- Declaración de 'suma' ---
            # 1: Aritmética local
            ("+", "a", "b", "t1"),
            # 2: Imprime
            ("PRINT", "t1", "_", "_"),
            # 3: Fin de función
            ("ENDFUNC", "_", "_", "_"),
            
            # --- Ejecución del inicio ---
            # 4: ERA
            ("ERA", "suma", "_", "_"),
            
            # 5: Evaluación y envío del primer parámetro
            ("PARAM", "5", "_", "param0"),
            
            # 6: Evaluación y envío del segundo parámetro
            ("PARAM", "10", "_", "param1"),
            
            # 7: GOSUB (Salta al índice 1)
            ("GOSUB", "suma", "_", 1)
        ]
    ),
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
            # 0: Salto inicial
            ("GOTO", "_", "_", 3),
            
            # --- Declaración de 'multiplica' ---
            # 1: Imprime local
            ("PRINT", "a", "_", "_"),
            # 2: Fin de función
            ("ENDFUNC", "_", "_", "_"),
            
            # --- Ejecución del inicio ---
            # 3: ERA
            ("ERA", "multiplica", "_", "_"),
            
            # 4: Parámetro
            ("PARAM", "5", "_", "param0"),
            
            # 5: GOSUB al índice 1
            ("GOSUB", "multiplica", "_", 1),
            
            # 6: Parche de extracción del retorno (generado por action_llamada_end)
            ("=", "multiplica", "_", "t1"),
            
            # 7: Continuación de la expresión principal (+ 2)
            ("+", "t1", "2", "t2"),
            
            # 8: Asignación final a la variable 'x'
            ("=", "t2", "_", "x")
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