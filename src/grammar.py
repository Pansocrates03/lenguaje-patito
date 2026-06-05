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
        Keyword("escribe") | Keyword("nula")
    )
    
    # TOKENS
    # Se definen los tokens básicos del lenguaje

    IDENTIFICADOR = ~PALABRAS_RESERVADAS + Word(alphas + "_", alphanums + "_")
    TIPO = Literal("entero") | Literal("flotante")
    CTE_ENTERA = Word(nums)
    CTE_FLOTANTE = Regex(r'\d+\.\d+')
    LETRERO = Literal('"') + ZeroOrMore(Word(alphanums + " ")) + Literal('"')

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
    ).addParseAction(actions["action_vars_decl"])
    VARSLIST = ZeroOrMore(VARS_LINE)
    VARS = Literal("vars") + VARSLIST

    CTE = CTE_FLOTANTE | CTE_ENTERA 
    

    # Camino 1: ( EXPRESION ) — con centinela
    abre_paren = Literal("(").copy().addParseAction(actions["action_factor_abre_paren"])
    factor_paren = (
        abre_paren
        + EXPRESION
        + Literal(")")   # sin acción — el pop del ( lo hace finalizar_expresion
    )

    # Camino 2: [+|-] id | CTE — con signo opcional
    factor_base = (
        Optional(Literal("+") | Literal("-")) + (IDENTIFICADOR | CTE)
    ).addParseAction(actions["action_factor_signo"])

    # FACTOR sin acción global — cada camino tiene la suya
    FACTOR = factor_paren | factor_base #| LLAMADA
        
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
        IDENTIFICADOR.copy().addParseAction(actions["action_asigna_id"])
        + Literal("=").addParseAction(actions["action_asigna_op"])
        + EXPRESION.copy().addParseAction(actions["action_asigna_end"])
        + Literal(";").addParseAction(actions["action_asigna_cierre"])
    )

    CONDICION = (
        Literal("si")
        + Literal("(")
        + EXPRESION.copy().addParseAction(actions["action_condicion_eval"]) # PN1
        + Literal(")")
        + CUERPO
        + Optional(
            Literal("sino").addParseAction(actions["action_condicion_sino"]) # PN2
            + CUERPO
        )
        + Literal(";")
    ).addParseAction(actions["action_condicion_end"]) # PN3

    CICLO = (
        Literal("mientras").addParseAction(actions["action_ciclo_inicio"])
        + Literal("(")
        + EXPRESION.copy().addParseAction(actions["action_ciclo_eval"])
        + Literal(")")
        + Literal("haz")
        + CUERPO
        + Literal(";").addParseAction(actions["action_ciclo_end"])
    )

    IMPRIME_ITEM = (LETRERO | EXPRESION).copy().addParseAction(actions["action_imprime_item"])
    IMPRIME = (
        Literal("escribe")
        + Literal("(")
        + IMPRIME_ITEM
        + ZeroOrMore(Literal(",") + IMPRIME_ITEM)
        + Literal(")")
        + Literal(";")
    )

    LLAMADA <<= (
        IDENTIFICADOR
        + Literal("(")
        + Optional(
            EXPRESION
            + ZeroOrMore(Literal(",") + EXPRESION)
        )
        + Literal(")").addParseAction(actions["test"])
    )

    ESTATUTO <<= ASIGNA | CONDICION | CICLO | (LLAMADA  + Literal(";")) | IMPRIME | (Literal("[") + ZeroOrMore(ESTATUTO) + Literal("]"))

    CUERPO <<= Literal("{") + ZeroOrMore(ESTATUTO) + Literal("}")

    PARAM = IDENTIFICADOR + Literal(":") + TIPO

    FUNCS = ZeroOrMore(
        (TIPO | Literal("nula")) 
        + IDENTIFICADOR
        + Literal("(")
        + Optional(
            PARAM + ZeroOrMore(Literal(",") + PARAM)
            )
        + Literal(")")
        + Literal("{") 
        + Optional(VARS)
        + CUERPO
        + Literal("}")
    )

    # Definir la estructura del programa
    lenguaje_patito = (
        Literal("programa")
        + IDENTIFICADOR
        + Literal(";")
        + Optional(VARS)
        + FUNCS
        + Literal("inicio")
        + CUERPO + Literal("fin")
    )
    
    return lenguaje_patito