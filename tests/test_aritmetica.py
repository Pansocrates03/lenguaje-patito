import pytest
from grammar import crear_gramática # Ignorar error
from semantic_context import SemanticContext # Ignorar error

# Helper para compilar código en crudo y extraer los cuádruplos generados
def compilar_y_obtener_cuadruplos(codigo: str) -> list:
    semantic = SemanticContext()
    # Inicializamos la gramática inyectando un contexto semántico limpio
    lenguaje_patito = crear_gramática(semantic)
    
    # parseString detona las acciones semánticas y llena la fila de cuádruplos
    lenguaje_patito.parseString(codigo)
    return semantic.obtener_cuadruplos()

@pytest.mark.parametrize("nombre_prueba, codigo, expected_ops", [
    (
        "Aritmetica Simple",
        """
        programa test_simple;
        inicio {
            escribe(5 + 3);
        } fin
        """,
        # Lista esperada de tuplas: (operador, operando1, operando2, resultado)
        [
            ("GOTO", "_", "_", 1),       # Salto inicial al final del inicio
            ("+", "5", "3", "t1"),
            ("PRINT", "t1", "_", "_")
        ]
    ),
    (
        "Aritmetica con Parentesis",
        """
        programa test_parentesis;
        inicio {
            escribe((5 + 3) * 2);
        } fin
        """,
        [
            ("GOTO", "_", "_", 1),       # Salto inicial al final del inicio
            ("+", "5", "3", "t1"),     # Resuelve primero el paréntesis
            ("*", "t1", "2", "t2"),    # Multiplica el temporal por 2
            ("PRINT", "t2", "_", "_")  # Imprime el temporal final
        ]
    ),
    (
        "Jerarquía de Operaciones",
        """
        programa test_jerarquia;
        inicio {
            escribe(10 - 4 / 2);
        } fin
        """,
        [
            ("GOTO", "_", "_", 1),       # Salto inicial al final del inicio
            ("/", "4", "2", "t1"),     # La división tiene mayor precedencia
            ("-", "10", "t1", "t2"),
            ("PRINT", "t2", "_", "_")
        ]
    )
])
def test_generacion_cuadruplos(nombre_prueba, codigo, expected_ops):
    # Act
    cuadruplos = compilar_y_obtener_cuadruplos(codigo)
    
    # Assert - Verificamos que se genere la cantidad correcta de cuádruplos
    assert len(cuadruplos) == len(expected_ops), \
        f"Fallo en {nombre_prueba}: Se esperaban {len(expected_ops)} cuádruplos, se obtuvieron {len(cuadruplos)}."
    
    # Assert - Verificamos el contenido exacto de cada cuádruplo
    for i, (cuadruplo, (exp_op, exp_op1, exp_op2, exp_res)) in enumerate(zip(cuadruplos, expected_ops)):
        assert cuadruplo.operador == exp_op, f"Operador incorrecto en cuádruplo {i}"
        assert str(cuadruplo.operando1) == exp_op1, f"Operando 1 incorrecto en cuádruplo {i}"
        assert str(cuadruplo.operando2) == exp_op2, f"Operando 2 incorrecto en cuádruplo {i}"
        assert cuadruplo.resultado == exp_res, f"Resultado incorrecto en cuádruplo {i}"