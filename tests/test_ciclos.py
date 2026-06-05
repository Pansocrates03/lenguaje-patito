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
        "Mientras con un solo estatuto",
        """
        programa test_mientras_simple;
        vars x: entero;
        inicio {
            x = 5;
            mientras (x > 0) haz {
                escribe(x);
            };
        } fin
        """,
        [
            # 0: Asignación inicial
            ("=", "5", "_", "x"),
            
            # 1: Evaluación de la condición (AQUÍ INICIA EL CICLO - PN1)
            (">", "x", "0", "t1"),
            
            # 2: Salto condicional si es falso. 
            # Brinca al cuádruplo 5 (fuera del ciclo) - PN2
            ("GOTOF", "t1", "_", 5),
            
            # 3: Cuerpo del ciclo
            ("PRINT", "x", "_", "_"),
            
            # 4: Fin del cuerpo. Salto incondicional al inicio (cuádruplo 1) - PN3
            ("GOTO", "_", "_", 1)
        ]
    ),
    (
        "Mientras con multiples estatutos en el cuerpo",
        """
        programa test_mientras_multiple;
        vars contador: entero;
        inicio {
            contador = 0;
            mientras (contador < 10) haz {
                escribe(contador);
                contador = contador + 1;
            };
        } fin
        """,
        [
            # 0: Asignación
            ("=", "0", "_", "contador"),
            
            # 1: Evaluación de la condición
            ("<", "contador", "10", "t1"),
            
            # 2: GOTOF. El ciclo ocupa más cuádruplos, ahora debe saltar al 7
            ("GOTOF", "t1", "_", 7),
            
            # 3: Cuerpo - imprime
            ("PRINT", "contador", "_", "_"),
            
            # 4: Cuerpo - suma aritmética
            ("+", "contador", "1", "t2"),
            
            # 5: Cuerpo - asignación de la suma al contador
            ("=", "t2", "_", "contador"),
            
            # 6: GOTO incondicional de regreso al inicio de la evaluación (1)
            ("GOTO", "_", "_", 1)
        ]
    )
])
def test_generacion_cuadruplos_mientras(nombre_prueba, codigo, expected_ops):
    # Act
    cuadruplos = compilar_y_obtener_cuadruplos(codigo)
    
    # Assert - Verificamos que se genere la cantidad correcta de cuádruplos
    assert len(cuadruplos) == len(expected_ops), \
        f"Fallo en {nombre_prueba}: Se esperaban {len(expected_ops)} cuádruplos, se obtuvieron {len(cuadruplos)}."
    
    # Assert - Verificamos el contenido exacto de cada cuádruplo
    for i, (cuadruplo, (exp_op, exp_op1, exp_op2, exp_res)) in enumerate(zip(cuadruplos, expected_ops)):
        assert cuadruplo.operador == exp_op, f"[{i}] Operador incorrecto: esperado '{exp_op}', obtenido '{cuadruplo.operador}'"
        assert str(cuadruplo.operando1) == exp_op1, f"[{i}] Operando 1 incorrecto: esperado '{exp_op1}', obtenido '{cuadruplo.operando1}'"
        assert str(cuadruplo.operando2) == exp_op2, f"[{i}] Operando 2 incorrecto: esperado '{exp_op2}', obtenido '{cuadruplo.operando2}'"
        assert cuadruplo.resultado == exp_res, f"[{i}] Resultado incorrecto: esperado '{exp_res}', obtenido '{cuadruplo.resultado}'"