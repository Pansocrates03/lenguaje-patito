from pyparsing import Optional, Word, ZeroOrMore, OneOrMore, Literal, alphas, alphanums, Forward, nums, Regex

# Definir gramática para el lenguaje patito
IDENTIFICADOR = Word(alphas + "_", alphanums + "_")
TIPO = Literal("entero") | Literal("flotante")
CTE_ENTERA = Word(nums)
CTE_FLOTANTE = Regex(r'\d+\.\d+')
LETRERO = Literal('"') + ZeroOrMore(Word(alphanums + " ")) + Literal('"')

########################################################

EXPRESION = Forward()
CUERPO = Forward()
ESTATUTO = Forward()
LLAMADA = Forward()

####################

VARSLIST = ZeroOrMore(IDENTIFICADOR + ZeroOrMore(Literal(",") + IDENTIFICADOR) + Literal(":") + TIPO + Literal(";"))
VARS = Optional(Literal("vars") + VARSLIST)

CTE = CTE_FLOTANTE | CTE_ENTERA 
FACTOR = (Literal("(") + EXPRESION + Literal(")")) | LLAMADA | (Optional(Literal("+") | Literal("-")) + (IDENTIFICADOR | CTE))
TERMINO = FACTOR + ZeroOrMore((Literal("*") | Literal("/")) + FACTOR)
EXP = TERMINO + ZeroOrMore((Literal("+") | Literal("-")) + TERMINO)
EXPRESION <<= EXP + Optional((Literal(">") | Literal("<") | Literal("!=") | Literal("=")) + EXP)
ASIGNA = IDENTIFICADOR + Literal("=") + EXPRESION + Literal(";")

CONDICION = Literal("si") + Literal("(") + EXPRESION + Literal(")") + CUERPO + Optional(Literal("sino") + CUERPO)

CICLO = Literal("mientras") + Literal("(") + EXPRESION + Literal(")") + CUERPO + Literal(";")

LLAMADA <<= IDENTIFICADOR + Literal("(") + Optional(EXPRESION + ZeroOrMore(Literal(",") + EXPRESION)) + Literal(")")

IMPRIME = Literal("escribe") + Literal("(") + (LETRERO | EXPRESION) + ZeroOrMore(Literal(",") + (LETRERO | EXPRESION)) + Literal(")") + Literal(";")

ESTATUTO <<= ASIGNA | CONDICION | CICLO | (LLAMADA  + Literal(";")) | IMPRIME | (Literal("[") + ZeroOrMore(ESTATUTO) + Literal("]"))

CUERPO <<= Literal("{") + ZeroOrMore(ESTATUTO) + Literal("}")

FUNCS = ZeroOrMore(
    (TIPO | Literal("nula")) + 
    IDENTIFICADOR +
    Literal("(") +
    Optional(
        IDENTIFICADOR + Literal(":") + TIPO + ZeroOrMore(Literal(",") + IDENTIFICADOR + Literal(":") + TIPO)
        ) +
    Literal(")") +
    Literal("{") + 
    Optional(VARS) +
    CUERPO +
    Literal("}")
)

# Definir la estructura del programa
lenguaje_patito = Literal("programa") + IDENTIFICADOR + Literal(";") + VARS +  FUNCS + Literal("inicio") + CUERPO + Literal("fin")