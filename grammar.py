from pyparsing import Optional, Suppress, Word, ZeroOrMore, OneOrMore, Literal, alphas, alphanums, Forward, nums, Regex, Group, delimitedList
from semantic_actions import make_actions

def crear_gramática(semantic_context):
    """Crea la gramática del lenguaje Patito con acciones semánticas"""

    actions = make_actions(semantic_context)
    
    # TOKENS
    # Se definen los tokens básicos del lenguaje

    IDENTIFICADOR = Word(alphas + "_", alphanums + "_")
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
    

    factor_base = (Literal("(") + EXPRESION + Literal(")")) | LLAMADA | (Optional(Literal("+") | Literal("-")) + (IDENTIFICADOR | CTE))
    FACTOR = factor_base.copy()
    FACTOR.setParseAction(actions["action_operando"])
        
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
            (Literal(">") | Literal("<") | Literal("!=") | Literal("=="))
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
        + EXPRESION 
        + Literal(")")
        + CUERPO
        + Optional(Literal("sino") + CUERPO)
    )

    CICLO = (
        Literal("mientras")
        + Literal("(")
        + EXPRESION
        + Literal(")")
        + CUERPO
        + Literal(";")
    )

    LLAMADA <<= (
        IDENTIFICADOR
        + Literal("(")
        + Optional(
            EXPRESION
            + ZeroOrMore(Literal(",") + EXPRESION)
        )
        + Literal(")")
    )

    IMPRIME = (
        Literal("escribe")
        + Literal("(")
        + (LETRERO | EXPRESION)
        + ZeroOrMore(Literal(",") + (LETRERO | EXPRESION))
        + Literal(")")
        + Literal(";")
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