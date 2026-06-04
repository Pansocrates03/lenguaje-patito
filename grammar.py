from pyparsing import Optional, Word, ZeroOrMore, OneOrMore, Literal, alphas, alphanums, Forward, nums, Regex, Group, delimitedList

def crear_gramática(semantic_context):
    """Crea la gramática del lenguaje Patito con acciones semánticas"""
    
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

    VARSLIST = ZeroOrMore(IDENTIFICADOR + ZeroOrMore(Literal(",") + IDENTIFICADOR) + Literal(":") + TIPO + Literal(";"))
    VARS = Optional(Literal("vars") + VARSLIST)

    CTE = CTE_FLOTANTE | CTE_ENTERA 
    
    # FACTOR con acción para capturar operandos
    def action_operando(s, l, tokens):
        # Extraer el operando (el último elemento que no sea un paréntesis o signo)
        token_list = list(tokens)
        for token in token_list:
            token_str = str(token).strip()
            if token_str not in ['(', ')', '+', '-', ''] and token_str:
                semantic_context.push_operando(token_str)
                break
        return tokens
    
    factor_base = (Literal("(") + EXPRESION + Literal(")")) | LLAMADA | (Optional(Literal("+") | Literal("-")) + (IDENTIFICADOR | CTE))
    FACTOR = factor_base.copy()
    FACTOR.setParseAction(action_operando)
    
    # Operadores de multiplicación y división
    mul_op = (Literal("*") | Literal("/"))
    def action_mul_op(s, l, tokens):
        semantic_context.push_operador(tokens[0])
        return tokens
    mul_op.setParseAction(action_mul_op)
    
    TERMINO = FACTOR + ZeroOrMore(mul_op + FACTOR)
    
    # Operadores de suma y resta
    add_op = (Literal("+") | Literal("-"))
    def action_add_op(s, l, tokens):
        semantic_context.push_operador(tokens[0])
        return tokens
    add_op.setParseAction(action_add_op)
    
    EXP = TERMINO + ZeroOrMore(add_op + TERMINO)
    
    def action_expresion_end(s, l, tokens):
        semantic_context.finalizar_expresion()
        return tokens
    
    comp_op = (Literal(">") | Literal("<") | Literal("!=") | Literal("=="))
    EXPRESION <<= (EXP + Optional(comp_op + EXP)).setParseAction(action_expresion_end)
    
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
    
    return lenguaje_patito