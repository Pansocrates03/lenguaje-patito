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
        "Condicion SI simple (sin SINO)",
        """
        programa test_si_simple;
        vars x: entero;
        inicio {
            x = 10;
            si (x > 5) {
                escribe(x);
            };
        } fin
        """,
        [
            # 0: Salto inicial al final del inicio
            ("GOTO", "_", "_", 1),       
            
            # 1: Asignación inicial
            ("=", "10", "_", "x"),
            
            # 2: Evaluación de la condición
            (">", "x", "5", "t1"),
            
            # 3: GOTOF (PN1). Brinca al cuádruplo 5 si la condición es falsa
            ("GOTOF", "t1", "_", 5),
            
            # 4: Cuerpo del 'si' verdadero
            ("PRINT", "x", "_", "_")
        ]
    ),
    (
        "Condicion SI / SINO completa",
        """
        programa test_si_sino;
        vars x: entero;
        inicio {
            x = 10;
            si (x > 5) {
                escribe(1);
            } sino {
                escribe(0);
            };
        } fin
        """,
        [
            # 0: Salto inicial
            ("GOTO", "_", "_", 1),
            
            # 1: Asignación inicial
            ("=", "10", "_", "x"),
            
            # 2: Evaluación de la condición
            (">", "x", "5", "t1"),
            
            # 3: GOTOF (PN1). Brinca al cuádruplo 6 si es falso (inicio del 'sino')
            ("GOTOF", "t1", "_", 6),
            
            # 4: Cuerpo del 'si' verdadero
            ("PRINT", "1", "_", "_"),
            
            # 5: GOTO incondicional (PN2). Brinca al cuádruplo 7 para esquivar el 'sino'
            ("GOTO", "_", "_", 7),
            
            # 6: Cuerpo del 'sino' falso
            ("PRINT", "0", "_", "_")
        ]
    ),
    (
        "Condiciones SI / SINO anidadas",
        """
        programa test_anidado;
        vars x: entero;
        inicio {
            x = 10;
            si (x > 5) {
                si (x == 10) {
                    escribe(10);
                };
            } sino {
                escribe(0);
            };
        } fin
        """,
        [
            # 0: Salto inicial
            ("GOTO", "_", "_", 1),       
            
            # 1: Asignación
            ("=", "10", "_", "x"),
            
            # 2: Evaluación primer 'si'
            (">", "x", "5", "t1"),
            
            # 3: GOTOF primer 'si' -> salta al 'sino' externo (cuádruplo 8)
            ("GOTOF", "t1", "_", 8),
            
            # 4: Evaluación 'si' interno
            ("==", "x", "10", "t2"),
            
            # 5: GOTOF 'si' interno -> salta fuera del 'si' interno (cuádruplo 7)
            ("GOTOF", "t2", "_", 7),
            
            # 6: Cuerpo del 'si' interno
            ("PRINT", "10", "_", "_"),
            
            # 7: GOTO incondicional del primer 'si' -> salta fuera de todo (cuádruplo 9)
            ("GOTO", "_", "_", 9),
            
            # 8: Cuerpo del 'sino' externo
            ("PRINT", "0", "_", "_")
        ]
    )
])
def test_generacion_cuadruplos_condicional(nombre_prueba, codigo, expected_ops):
    # Act
    cuadruplos = compilar_y_obtener_cuadruplos(codigo)
    
    # Assert - Verificamos cantidad
    assert len(cuadruplos) == len(expected_ops), f"Fallo en {nombre_prueba}: Se esperaban {len(expected_ops)} cuádruplos, se obtuvieron {len(cuadruplos)}."
    
    # Assert - Verificamos cada instrucción
    for i, (cuadruplo, (exp_op, exp_op1, exp_op2, exp_res)) in enumerate(zip(cuadruplos, expected_ops)):
        assert cuadruplo.operador == exp_op, f"[{i}] Operador incorrecto: esperado '{exp_op}', obtenido '{cuadruplo.operador}'"
        assert str(cuadruplo.operando1) == exp_op1, f"[{i}] Operando 1 incorrecto: esperado '{exp_op1}', obtenido '{cuadruplo.operando1}'"
        assert str(cuadruplo.operando2) == exp_op2, f"[{i}] Operando 2 incorrecto: esperado '{exp_op2}', obtenido '{cuadruplo.operando2}'"
        assert cuadruplo.resultado == exp_res, f"[{i}] Resultado incorrecto: esperado '{exp_res}', obtenido '{cuadruplo.resultado}'"