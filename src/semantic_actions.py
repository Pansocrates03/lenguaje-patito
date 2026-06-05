from semantic_context import Cuadruplo

def make_actions(ctx):
    """
    Fábrica de acciones semánticas para la gramática de Patito.
    Recibe el SemanticContext y regresa todas las funciones action_*
    como un diccionario, listas para asignarse con setParseAction.
    """

    # ── EXPRESIÓN ────────────────────────────────────────────────────────────

    def action_operando(s, l, tokens):
        """
        PN — Al reconocer un FACTOR (identificador o constante).
        Empuja el operando a pila_operandos y su tipo a pila_tipos.
        Ignora paréntesis y signos unarios.
        """
        token_list = list(tokens)
        for token in token_list:
            token_str = str(token).strip()
            if token_str not in ['(', ')', '+', '-', ''] and token_str:
                ctx.push_operando(token_str)
                print(f"DEBUG operando - empujé: {token_str}")
                print(f"DEBUG operando - pila_operandos: {ctx.pila_operandos}")
                print(f"DEBUG operando - pila_tipos: {ctx.pila_tipos}")
                break
        return tokens

    def action_mul_op(s, l, tokens):
        """
        PN — Al reconocer * o /.
        Empuja el operador a pila_operadores.
        """
        ctx.push_operador(tokens[0])
        return tokens

    def action_add_op(s, l, tokens):
        """
        PN — Al reconocer + o -.
        Empuja el operador a pila_operadores.
        """
        ctx.push_operador(tokens[0])
        return tokens
    
    def action_rel_op(s, l, tokens):
        """
        PN — Al reconocer >, <, != o ==.
        Empuja el operador relacional a pila_operadores.
        """
        ctx.push_operador(tokens[0])
        return tokens

    def action_expresion_end(s, l, tokens):
        """
        PN — Al terminar una EXPRESIÓN completa.
        Resuelve operadores pendientes y genera cuádruplos intermedios.
        """
        ctx.finalizar_expresion()
        return tokens
    
    def action_factor_abre_paren(s, l, tokens):
        """
        PN — Al reconocer un paréntesis de apertura en un FACTOR.
        Empuja el paréntesis a pila_operadores para marcar el inicio de la subexpresión.
        """
        print(f"DEBUG abre_paren - pila_operadores antes: {ctx.pila_operadores}")
        ctx.pila_operadores.append("(")
        print(f"DEBUG abre_paren - pila_operadores después: {ctx.pila_operadores}")
        return tokens
    
    def action_factor_cierra_paren(s, l, tokens):
        """
        PN — Al reconocer un paréntesis de cierre en un FACTOR.
        Resuelve operadores pendientes hasta encontrar el paréntesis de apertura.
        Elimina el paréntesis de apertura de pila_operadores.
        """
        print(f"DEBUG cierra_paren - pila_operadores antes: {ctx.pila_operadores}")
        while ctx.pila_operadores and ctx.pila_operadores[-1] != "(":
            ctx.ejecutar_operacion()
        ctx.pila_operadores.pop()  # quitar el "("
        print(f"DEBUG cierra_paren - pila_operadores después: {ctx.pila_operadores}")
        return tokens
    
    def action_factor_signo(s, l, tokens):
        print(f"DEBUG factor_signo tokens: {list(tokens)}")
        token_list = list(tokens)
        
        # Identificar si hay signo y cuál es el operando
        if len(token_list) == 2 and token_list[0] in ["+", "-"]:
            signo   = token_list[0]
            operando = token_list[1]
        else:
            signo    = None
            operando = token_list[0]

        # push_operando ya determina el tipo internamente
        ctx.push_operando(operando)

        # Si hay signo negativo, generar cuádruplo (*, -1, operando, t1)
        if signo == "-":
            op = ctx.pila_operandos.pop()
            tp = ctx.pila_tipos.pop()
            resultado = ctx.nuevo_temporal()
            ctx.fila_cuadruplos.append(Cuadruplo("*", "-1", op, resultado))
            ctx.pila_operandos.append(resultado)
            ctx.pila_tipos.append(tp)

        return tokens

    # ── ASIGNA ───────────────────────────────────────────────────────────────

    def action_asigna_id(s, l, tokens):
        nombre = tokens[0]
        tipo = None

        # 1. Buscar en scope local si estamos dentro de una función
        if ctx.funcion_en_construccion:
            tabla_local = ctx.funcion_en_construccion.get("variables", {})
            params_local = {p["nombre"]: p["tipo"] for p in ctx.funcion_en_construccion.get("parametros", [])}
            if nombre in tabla_local:
                tipo = tabla_local[nombre]
            elif nombre in params_local:
                tipo = params_local[nombre]

        # 2. Siempre buscar en scope global como fallback
        if tipo is None:
            tabla_global = ctx.directorio_funciones[0].get("variables", {})
            if nombre in tabla_global:
                tipo = tabla_global[nombre]

        # 3. Si no existe en ningún lado, error
        if tipo is None:
            raise Exception(f"Variable '{nombre}' no declarada")

        ctx.pila_operandos.append(nombre)
        ctx.pila_tipos.append(tipo)

        print(f"DEBUG asigna_id - empujé: {nombre} tipo: {tipo}")
        print(f"DEBUG asigna_id - pila_operandos: {ctx.pila_operandos}")
        print(f"DEBUG asigna_id - pila_tipos: {ctx.pila_tipos}")
        return tokens

    def action_asigna_op(s, l, tokens):
        """
        PN2 — Al reconocer el operador =.
        Registra la intención de asignación en pila_operadores.
        No genera cuádruplo todavía.
        """
        ctx.push_operador(tokens[0])
        return tokens

    def action_asigna_end(s, l, tokens):
        print(f"DEBUG asigna_end - pila_operandos: {ctx.pila_operandos}")
        print(f"DEBUG asigna_end - pila_tipos: {ctx.pila_tipos}")
        print(f"DEBUG asigna_end - pila_operadores: {ctx.pila_operadores}")
        if len(ctx.pila_tipos) < 2:
            raise Exception("Error de tipos: no hay suficientes tipos en la pila")
        
        tipo_derecho   = ctx.pila_tipos.pop()
        tipo_izquierdo = ctx.pila_tipos.pop()

        tipo_resultado = ctx.tipo_resultado(tipo_izquierdo, "=", tipo_derecho)

        if len(ctx.pila_operandos) < 2:
            raise Exception("Error de operandos: no hay suficientes operandos en la pila")

        resultado  = ctx.pila_operandos.pop()
        id_destino = ctx.pila_operandos.pop()

        # ✅ Desapilar el "=" que empujó action_asigna_op
        ctx.pila_operadores.pop()

        ctx.fila_cuadruplos.append(Cuadruplo("=", resultado, "_", id_destino))
        ctx.pila_tipos.append(tipo_resultado)

        return tokens

    def action_asigna_cierre(s, l, tokens):
        # Limpiar el tipo resultado que quedó de action_asigna_end
        if ctx.pila_tipos:
            ctx.pila_tipos.pop()

        if len(ctx.pila_operandos) != 0:
            raise Exception(f"Error: pila_operandos no quedó vacía al cerrar asignación, contiene: {ctx.pila_operandos}")
        
        if len(ctx.pila_operadores) != 0:
            raise Exception(f"Error: pila_operadores no quedó vacía al cerrar asignación, contiene: {ctx.pila_operadores}")
        
        if len(ctx.pila_tipos) != 0:
            raise Exception(f"Error: pila_tipos no quedó vacía al cerrar asignación, contiene: {ctx.pila_tipos}")

        if len(ctx.fila_cuadruplos) == 0:
            raise Exception("Error: no se emitió ningún cuádruplo para la asignación")

        ultimo_cuadruplo = ctx.fila_cuadruplos[-1]
        if ultimo_cuadruplo.operador != "=":
            raise Exception(f"Error: el último cuádruplo emitido no es una asignación, es: {ultimo_cuadruplo}")

        return tokens

    # ── CONDICION (si / sino) ─────────────────────────────────────────────────

    def action_condicion_eval(s, l, tokens):
        """
        PN — Al terminar la EXPRESIÓN de la condición del 'si'.
        Genera cuádruplo GOTOF y empuja la posición a pila_saltos.
        """
        tipo_res = ctx.pila_tipos.pop()
        if tipo_res != "bool":
            raise Exception("Error semántico: La condición del 'si' debe ser booleana.")

        resultado = ctx.pila_operandos.pop()
        
        # Generar GOTOF con destino pendiente
        ctx.fila_cuadruplos.append(Cuadruplo("GOTOF", resultado, "_", "_"))
        
        # Guardar la posición para rellenarlo después
        ctx.pila_saltos.append(len(ctx.fila_cuadruplos) - 1)
        return tokens

    def action_condicion_sino(s, l, tokens):
        """
        PN — Al reconocer 'sino'.
        Genera cuádruplo GOTO para saltar el bloque sino,
        rellena el GOTOF pendiente en pila_saltos.
        """
        # 1. Generar GOTO incondicional para brincar el bloque falso
        ctx.fila_cuadruplos.append(Cuadruplo("GOTO", "_", "_", "_"))
        
        # 2. Rescatar el GOTOF pendiente del si
        falso = ctx.pila_saltos.pop()
        
        # 3. Empujar el nuevo GOTO incondicional a la pila
        ctx.pila_saltos.append(len(ctx.fila_cuadruplos) - 1)
        
        # 4. Rellenar el destino del GOTOF hacia este bloque
        ctx.fila_cuadruplos[falso].resultado = len(ctx.fila_cuadruplos)
        return tokens

    def action_condicion_end(s, l, tokens):
        """
        PN — Al cerrar el bloque del 'si' (o 'sino').
        Rellena el GOTO o GOTOF pendiente en pila_saltos con
        el contador de cuádruplos actual.
        """
        # Sacar el salto pendiente (ya sea el GOTOF inicial o el GOTO del sino)
        fin = ctx.pila_saltos.pop()
        
        # Rellenarlo con el cuádruplo actual
        ctx.fila_cuadruplos[fin].resultado = len(ctx.fila_cuadruplos)
        return tokens

    # ── CICLO (mientras) ──────────────────────────────────────────────────────

    def action_ciclo_inicio(s, l, tokens):
        """
        PN — Al reconocer 'mientras', antes de evaluar la condición.
        Guarda la posición actual del contador de cuádruplos en pila_saltos
        para saber a dónde regresar al final del ciclo.
        """
        ctx.pila_saltos.append(len(ctx.fila_cuadruplos))
        return tokens

    def action_ciclo_eval(s, l, tokens):
        """
        PN — Al terminar la EXPRESIÓN de la condición del ciclo.
        Genera cuádruplo GOTOF y empuja su posición a pila_saltos.
        """
        # 1. Verificar tipo de la expresión
        tipo_res = ctx.pila_tipos.pop()
        if tipo_res != "bool":
            raise Exception("Error semántico: La condición del ciclo 'mientras' debe ser booleana.")

        # 2. Obtener el resultado de la evaluación
        resultado = ctx.pila_operandos.pop()

        # 3. Generar cuádruplo GOTOF con destino pendiente ("_")
        ctx.fila_cuadruplos.append(Cuadruplo("GOTOF", resultado, "_", "_"))
        
        # 4. Guardar la posición de este GOTOF para rellenarlo al final
        ctx.pila_saltos.append(len(ctx.fila_cuadruplos) - 1)
        
        return tokens

    def action_ciclo_end(s, l, tokens):
        """
        PN — Al reconocer el ; que cierra el 'mientras'.
        Genera cuádruplo GOTO al inicio del ciclo,
        rellena el GOTOF pendiente en pila_saltos.
        """
        # 1. Sacar el índice del GOTOF pendiente de la pila
        falso = ctx.pila_saltos.pop()
        
        # 2. Sacar el índice de retorno (al inicio del ciclo)
        retorno = ctx.pila_saltos.pop()

        # 3. Generar GOTO incondicional para repetir el ciclo
        ctx.fila_cuadruplos.append(Cuadruplo("GOTO", "_", "_", retorno))

        # 4. Rellenar el salto pendiente del GOTOF
        # El destino es el cuádruplo actual (el que sigue después del GOTO)
        ctx.fila_cuadruplos[falso].resultado = len(ctx.fila_cuadruplos)
        return tokens

    # ── LLAMADA A FUNCIÓN ─────────────────────────────────────────────────────

    def action_llamada_inicio(s, l, tokens):
        """
        PN — Al reconocer el identificador de la función llamada.
        Verifica que la función exista en directorio_funciones.
        """
        # ejecutar PN llamada_inicio...
        return tokens

    def action_llamada_arg(s, l, tokens):
        """
        PN — Al terminar cada argumento de la llamada.
        Verifica tipo del argumento contra la firma de la función
        y genera cuádruplo PARAM.
        """
        # ejecutar PN llamada_arg...
        return tokens

    def action_llamada_end(s, l, tokens):
        """
        PN — Al cerrar el ) de la llamada.
        Verifica que el número de argumentos coincida con la firma
        y genera cuádruplo GOSUB.
        """
        # ejecutar PN llamada_end...
        return tokens

    # ── IMPRIME ───────────────────────────────────────────────────────────────

    def action_imprime_item(s, l, tokens):
        """
        PN — Al terminar cada ítem dentro de escribe(...).
        Genera cuádruplo PRINT para el valor o letrero correspondiente.
        """
        # El resultado de la expresión ya está resuelto en pila_operandos
        if ctx.pila_operandos:
            valor = ctx.pila_operandos.pop()
            ctx.pila_tipos.pop()  # limpiar el tipo correspondiente
        else:
            # Es un letrero (string literal)
            valor = tokens[0]

        ctx.fila_cuadruplos.append(Cuadruplo("PRINT", valor, "_", "_"))
        
        return tokens

    # ── DECLARACIÓN DE VARIABLES ──────────────────────────────────────────────

    def action_vars_decl(s, l, tokens):
        token_list = list(tokens)
        print(f"DEBUG vars_decl tokens: {token_list}")
        
        # El último token es el tipo, todo lo anterior son identificadores
        var_type = token_list[-1]
        
        if var_type not in ["entero", "flotante"]:
            raise Exception(f"Error: tipo inválido '{var_type}'")

        for token in token_list[:-1]:
            if ctx.funcion_en_construccion:
                ctx.funcion_en_construccion["variables"][token] = var_type
            else:
                ctx.directorio_funciones[0]["variables"][token] = var_type

        return tokens

    # ── FUNCIONES ─────────────────────────────────────────────────────────────

    def action_funcion_inicio(s, l, tokens):
        """
        PN — Al reconocer el encabezado de una función (tipo nombre (...)).
        Crea una nueva entrada en directorio_funciones y la marca
        como funcion_en_construccion en el contexto.
        """
        # ejecutar PN funcion_inicio...
        return tokens

    def action_funcion_end(s, l, tokens):
        """
        PN — Al cerrar el } de la función.
        Genera cuádruplo ENDFUNC, cierra funcion_en_construccion
        y limpia la tabla de variables locales.
        """
        # ejecutar PN funcion_end...
        return tokens

    # ── EXPORTAR ──────────────────────────────────────────────────────────────

    return {
        # Expresión aritmética / relacional
        "action_operando":      action_operando,
        "action_mul_op":        action_mul_op,
        "action_add_op":        action_add_op,
        "action_rel_op":        action_rel_op,
        "action_expresion_end": action_expresion_end,
        "action_factor_abre_paren": action_factor_abre_paren,
        "action_factor_cierra_paren": action_factor_cierra_paren,
        "action_factor_signo": action_factor_signo,
        # Asignación
        "action_asigna_id":     action_asigna_id,
        "action_asigna_op":     action_asigna_op,
        "action_asigna_end":    action_asigna_end,
        "action_asigna_cierre": action_asigna_cierre,
        # Condicional
        "action_condicion_eval": action_condicion_eval,
        "action_condicion_sino": action_condicion_sino,
        "action_condicion_end":  action_condicion_end,
        # Ciclo
        "action_ciclo_inicio":  action_ciclo_inicio,
        "action_ciclo_eval":    action_ciclo_eval,
        "action_ciclo_end":     action_ciclo_end,
        # Llamada
        "action_llamada_inicio": action_llamada_inicio,
        "action_llamada_arg":    action_llamada_arg,
        "action_llamada_end":    action_llamada_end,
        # Imprime
        "action_imprime_item":  action_imprime_item,
        # Declaraciones y funciones
        "action_vars_decl":     action_vars_decl,
        "action_funcion_inicio": action_funcion_inicio,
        "action_funcion_end":   action_funcion_end,
        # Test
        "test": lambda s, l, t: print(f"DEBUG test action triggered with tokens: {t}")
    }