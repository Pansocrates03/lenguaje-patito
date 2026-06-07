from pyparsing import Keyword, Optional, Suppress, Word, ZeroOrMore, OneOrMore, Literal, alphas, alphanums, Forward, nums, Regex, Group, delimitedList
from semantic_actions import make_actions

def crear_gramática(semantic_context):
    """Crea la gramática del lenguaje Patito con acciones semánticas"""

    actions = make_actions(semantic_context)

    # Palabras reservadas
    PALABRAS_RESERVADAS = (
        Keyword("programa") | Keyword("vars") | Keyword("entero") | 
        Keyword("flotante") | Keyword("inicio") | Keyword("fin") |
        Keyword("si") | Keyword("sino") | Keyword("mientras") | 
        Keyword("escribe") | Keyword("nula") | Keyword("regresa")
    )
    
    # TOKENS
    # Se definen los tokens básicos del lenguaje

    IDENTIFICADOR = ~PALABRAS_RESERVADAS + Word(alphas + "_", alphanums + "_")
    TIPO = Literal("entero") | Literal("flotante")
    CTE_ENTERA = Word(nums)
    CTE_FLOTANTE = Regex(r'\d+\.\d+')
    LETRERO = Regex(r'"[^"]*"')

    # FOWARDING
    # Se necesitan para definir reglas recursivas como EXPRESION y CUERPO

    EXPRESION = Forward()
    CUERPO = Forward()
    ESTATUTO = Forward()
    LLAMADA = Forward()

    # Variables globales para la semántica

    # Suprimir tokens que no nos interesan en vars
    VARS_LINE = (
        IDENTIFICADOR
        + ZeroOrMore(Suppress(Literal(",")) + IDENTIFICADOR)
        + Suppress(Literal(":"))
        + TIPO
        + Suppress(Literal(";"))
    ).add_parse_action(actions["action_vars_decl"])
    VARSLIST = ZeroOrMore(VARS_LINE)
    VARS = Literal("vars") + VARSLIST

    CTE = CTE_FLOTANTE | CTE_ENTERA 
    

    # Camino 1: ( EXPRESION ) — con centinela
    abre_paren = Literal("(").copy().add_parse_action(actions["action_factor_abre_paren"])
    factor_paren = (
        abre_paren
        + EXPRESION
        + Literal(")")
    ).add_parse_action(actions["action_factor_cierra_paren"])

    # Camino 2: [+|-] id | CTE — con signo opcional
    factor_base = (
        Optional(Literal("+") | Literal("-")) + (IDENTIFICADOR | CTE)
    ).add_parse_action(actions["action_factor_signo"])

    # FACTOR sin acción global — cada camino tiene la suya
    FACTOR = factor_paren | LLAMADA | factor_base
        
    TERMINO = (
        FACTOR
        + ZeroOrMore(
            (Literal("*") | Literal("/")).setParseAction(actions["action_mul_op"])
            + FACTOR
        )
    )
    
    EXP = (
        TERMINO
        + ZeroOrMore(
            (Literal("+") | Literal("-")).setParseAction(actions["action_add_op"])
            + TERMINO))
    
    EXPRESION <<= (
        EXP
        + Optional(
            (Literal(">") | Literal("<") | Literal("!=") | Literal("==")).setParseAction(actions["action_rel_op"])
            + EXP
        )
    ).setParseAction(actions["action_expresion_end"])
    
    ASIGNA = (
        IDENTIFICADOR.copy().add_parse_action(actions["action_asigna_id"])
        + Literal("=").add_parse_action(actions["action_asigna_op"])
        + EXPRESION.copy().add_parse_action(actions["action_asigna_end"])
        + Literal(";").add_parse_action(actions["action_asigna_cierre"])
    )

    CONDICION = (
        Literal("si")
        + Literal("(")
        + EXPRESION.copy().add_parse_action(actions["action_condicion_eval"]) # PN1
        + Literal(")")
        + CUERPO
        + Optional(
            Literal("sino").add_parse_action(actions["action_condicion_sino"]) # PN2
            + CUERPO
        )
        + Literal(";")
    ).add_parse_action(actions["action_condicion_end"]) # PN3

    CICLO = (
        Literal("mientras").add_parse_action(actions["action_ciclo_inicio"])
        + Literal("(")
        + EXPRESION.copy().add_parse_action(actions["action_ciclo_eval"])
        + Literal(")")
        + Literal("haz")
        + CUERPO
        + Literal(";").add_parse_action(actions["action_ciclo_end"])
    )

    IMPRIME_ITEM = (LETRERO | EXPRESION).copy().add_parse_action(actions["action_imprime_item"])
    IMPRIME = (
        Literal("escribe")
        + Literal("(")
        + IMPRIME_ITEM
        + ZeroOrMore(Literal(",") + IMPRIME_ITEM)
        + Literal(")")
        + Literal(";")
    )

    # 1. Agrupamos el ID y el ( para que la acción reciba ambos tokens juntos
    LLAMADA_INICIO = (
        IDENTIFICADOR 
        + Literal("(")
    ).add_parse_action(actions["action_llamada_inicio"])
    
    # 2. Tu argumento con su acción para los parámetros
    ARGUMENTO = EXPRESION.copy().add_parse_action(actions["action_llamada_arg"])

    # 3. La regla completa reconstruida
    LLAMADA <<= (
        LLAMADA_INICIO
        + Optional(
            ARGUMENTO
            + ZeroOrMore(Literal(",") + ARGUMENTO)
        )
        + Literal(")").add_parse_action(actions["action_llamada_end"])
    )

    REGRESA = (
        Literal('regresa')
        + EXPRESION.copy().addParseAction(actions["action_regresa"])
        + Literal(';')
    )

    ESTATUTO <<= (
        (LLAMADA  + Literal(";"))
        | CONDICION
        | CICLO
        | ASIGNA
        | IMPRIME
        | REGRESA
        | (Literal("[") + ZeroOrMore(ESTATUTO) + Literal("]"))
    )

    CUERPO <<= Literal("{") + ZeroOrMore(ESTATUTO) + Literal("}")

    PARAM = (
        IDENTIFICADOR
        + Literal(":")
        + TIPO
    ).add_parse_action(actions["action_funcion_param"])

    # Atamos el PN1 exclusivamente al tipo y nombre, ANTES de leer los paréntesis
    ENCABEZADO_FUNC = (
        (TIPO | Literal("nula")) 
        + IDENTIFICADOR
    ).add_parse_action(actions["action_funcion_inicio"])

    FUNCS = (
        ENCABEZADO_FUNC
        + Literal("(")
        + Optional(
            PARAM + ZeroOrMore(Literal(",") + PARAM)
            )
        + Literal(")")
        + Literal("{") 
        + Optional(VARS)
        + CUERPO
        + Literal("}")
        + Literal(";")
    ).add_parse_action(actions["action_funcion_end"])

    # Definir la estructura del programa
    lenguaje_patito = (
        Literal("programa").add_parse_action(actions["action_programa_inicio"])
        + IDENTIFICADOR
        + Literal(";")
        + Optional(VARS)
        + ZeroOrMore(FUNCS)
        + Literal("inicio").add_parse_action(actions["action_main_inicio"])
        + CUERPO
        + Literal("fin")
    )
    
    return lenguaje_patito