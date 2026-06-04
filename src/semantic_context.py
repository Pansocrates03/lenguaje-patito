class Cuadruplo:
    def __init__(self, operador, operando1=None, operando2=None, resultado=None):
        self.operador = operador
        self.operando1 = operando1
        self.operando2 = operando2
        self.resultado = resultado

    def __str__(self):
        return f"({self.operador}, {self.operando1}, {self.operando2}, {self.resultado})"

class SemanticContext:
    def __init__(self):
        # Pilas
        self.pila_operandos = []
        self.pila_operadores = []
        self.pila_tipos = []
        self.pila_saltos = []

        #Cuadruplos
        self.fila_cuadruplos: list[Cuadruplo] = []
        self.contador_temp = 0

        self.directorio_funciones = [
            {
                "nombre": "global",
                "tipo": None,
                "variables": {}
            }
        ]
        self.funcion_en_construccion = None

        # Cubo semántico: (tipo1, operador, tipo2) -> tipo_resultado | None
        self.cubo_semantico = {
            # ── Aritméticos ──────────────────────────────
            ("entero",   "+", "entero"):   "entero",
            ("flotante", "+", "flotante"): "flotante",
            ("entero",   "+", "flotante"): "flotante",
            ("flotante", "+", "entero"):   "flotante",

            ("entero",   "-", "entero"):   "entero",
            ("flotante", "-", "flotante"): "flotante",
            ("entero",   "-", "flotante"): "flotante",
            ("flotante", "-", "entero"):   "flotante",

            ("entero",   "*", "entero"):   "entero",
            ("flotante", "*", "flotante"): "flotante",
            ("entero",   "*", "flotante"): "flotante",
            ("flotante", "*", "entero"):   "flotante",

            ("entero",   "/", "entero"):   "entero",
            ("flotante", "/", "flotante"): "flotante",
            ("entero",   "/", "flotante"): "flotante",
            ("flotante", "/", "entero"):   "flotante",

            # ── Comparación ──────────────────────────────
            ("entero",   "==", "entero"):   "bool",
            ("flotante", "==", "flotante"): "bool",
            ("entero",   "!=", "entero"):   "bool",
            ("flotante", "!=", "flotante"): "bool",
            ("entero",   ">",  "entero"):   "bool",
            ("flotante", ">",  "flotante"): "bool",
            ("entero",   "<",  "entero"):   "bool",
            ("flotante", "<",  "flotante"): "bool",

            # ── Asignación ──────────────────────────────
            ("entero",   "=", "entero"):   "entero",
            ("flotante", "=", "flotante"): "flotante",
            #("entero",   "=", "flotante"): "flotante",  # entero no puede recibir flotante
            ("flotante", "=", "entero"):   "flotante",
        }

    def reset(self):
        self.pila_operandos.clear()
        self.pila_operadores.clear()
        self.pila_tipos.clear()
        self.pila_saltos.clear()
        self.fila_cuadruplos.clear()
        self.contador_temp = 0
        self.directorio_funciones = [
            {
                "nombre": "global",
                "tipo": None,
                "variables": {}
            }
        ]
        self.funcion_en_construccion = None

    def nuevo_temporal(self):
        self.contador_temp += 1
        temporal_name = f"t{self.contador_temp}"
        return temporal_name

    def precedencia(self, operador):
        precedencias = {
            "*": 2,
            "/": 2,
            "-": 1,
            "+": 1,
            ">": 0,
            "<": 0,
            "==": 0,
            "!=": 0,
            "_": -1
        }
        return precedencias.get(operador, 0)

    # ── push ─────────────────────────────────────────────────────────────────

    def push_operando(self, operando):
        self.pila_operandos.append(operando)

        # Determinar el tipo del operando
        if operando.lstrip('+-').isdigit():
            # 1. Constante entera
            self.pila_tipos.append("entero")
        elif self._es_flotante(operando):
            # 2. Constante flotante
            self.pila_tipos.append("flotante")
        else:
            # 3. Identificador — buscar en directorio
            tipo = self._buscar_tipo_variable(operando)
            self.pila_tipos.append(tipo)

    def push_operador(self, operador):
        # Respetar precedencia: ejecutar operaciones pendientes de mayor o igual precedencia
        while (self.pila_operadores
           and self.pila_operadores[-1] != "="
           and self.pila_operadores[-1] != "("   # ← agregar esta condición
           and self.precedencia(self.pila_operadores[-1]) >= self.precedencia(operador)):
            self.ejecutar_operacion()
        self.pila_operadores.append(operador)

    def push_tipo(self, tipo):
        self.pila_tipos.append(tipo)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _es_flotante(self, valor):
        try:
            float(valor)
            return '.' in valor
        except ValueError:
            return False

    def _buscar_tipo_variable(self, nombre):
        # Buscar en scope local primero
        if self.funcion_en_construccion:
            tabla_local = self.funcion_en_construccion.get("variables", {})
            if nombre in tabla_local:
                return tabla_local[nombre]
            params = {p["nombre"]: p["tipo"] for p in self.funcion_en_construccion.get("parametros", [])}
            if nombre in params:
                return params[nombre]

        # Buscar en scope global
        tabla_global = self.directorio_funciones[0].get("variables", {})
        if nombre in tabla_global:
            return tabla_global[nombre]

        raise Exception(f"Variable '{nombre}' no declarada")

    def tipo_resultado(self, tipo1, operador, tipo2):
        resultado = self.cubo_semantico.get((tipo1, operador, tipo2))
        if resultado is None:
            raise Exception(f"Operación inválida: {tipo1} {operador} {tipo2}")
        return resultado

    # ── operaciones ──────────────────────────────────────────────────────────

    def ejecutar_operacion(self):
        print(f"DEBUG ejecutar_op - pila_operadores: {self.pila_operadores}")
        print(f"DEBUG ejecutar_op - pila_operandos: {self.pila_operandos}")
        print(f"DEBUG ejecutar_op - pila_tipos: {self.pila_tipos}")
        """Genera un cuádruplo para la operación en la cima de pila_operadores"""
        if not self.pila_operadores or len(self.pila_operandos) < 2:
            return
        if len(self.pila_tipos) < 2:
            return

        operador  = self.pila_operadores.pop()
        tipo2     = self.pila_tipos.pop()
        tipo1     = self.pila_tipos.pop()
        operando2 = self.pila_operandos.pop()
        operando1 = self.pila_operandos.pop()

        # Verificar compatibilidad de tipos con el cubo semántico
        tipo_res = self.tipo_resultado(tipo1, operador, tipo2)

        # Crear temporal para almacenar el resultado
        resultado = self.nuevo_temporal()

        # Emitir cuádruplo
        self.fila_cuadruplos.append(Cuadruplo(operador, operando1, operando2, resultado))

        # El temporal vuelve a la pila como operando para la siguiente operación
        self.pila_operandos.append(resultado)
        self.pila_tipos.append(tipo_res)

    def finalizar_expresion(self):
        """Procesa todos los operadores pendientes al final de una expresión"""
        while self.pila_operadores and self.pila_operadores[-1] != "=" and self.pila_operadores[-1] != "(":
            self.ejecutar_operacion()
        
        # Si hay un ( en la cima, significa que terminamos la subexpresión — eliminarlo
        if self.pila_operadores and self.pila_operadores[-1] == "(":
            self.pila_operadores.pop()

    def obtener_cuadruplos(self):
        """Retorna la lista de cuádruplos generados"""
        return self.fila_cuadruplos