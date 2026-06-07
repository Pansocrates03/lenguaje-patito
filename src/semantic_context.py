class Funcion:
    def __init__(self, nombre, tipo=None):
        self.nombre = nombre
        self.tipo = tipo
        self.parametros = []
        self.variables = {}
        self.cuadruplo_inicio = None

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
        self.pila_llamadas = []  # Para manejar contextos de llamadas a funciones

        #Cuadruplos
        self.fila_cuadruplos: list[Cuadruplo] = []

        # Contador de temporales
        self.contador_temp = 0
        self.contador_global_entero = 1000
        self.contador_global_flotante = 2000
        self.contador_local_entero = 3000
        self.contador_local_flotante = 4000
        self.contador_temporal_entero = 5000
        self.contador_temporal_flotante = 6000
        self.contador_temporal_booleano = 7000
        self.contador_constantes_enteras = 8000
        self.contador_constantes_flotantes = 9000

        self.tabla_constantes = {} # Formato: {"10": 8000, "3.14": 9000}


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
        self.pila_llamadas.clear()
        self.fila_cuadruplos.clear()
        
        # Reiniciar contadores
        self.contador_temp = 0
        self.contador_temporal_entero = 5000
        self.contador_temporal_flotante = 6000
        self.contador_temporal_booleano = 7000
        self.contador_constantes_enteras = 8000
        self.contador_constantes_flotantes = 9000
        
        # Limpiar tabla de constantes
        self.tabla_constantes.clear()
        
        self.directorio_funciones = [
            {
                "nombre": "global",
                "tipo": None,
                "variables": {}
            }
        ]
        self.funcion_en_construccion = None

    def nuevo_temporal(self, tipo:str):

        if tipo == 'entero':
            dir_temp = self.contador_temporal_entero
            self.contador_temporal_entero += 1
            return dir_temp

        if tipo == 'flotante':
            dir_temp = self.contador_temporal_flotante
            self.contador_temporal_flotante += 1
            return dir_temp
        
        if tipo == 'bool':
            dir_temp = self.contador_temporal_booleano
            self.contador_temporal_booleano += 1  # <-- ¡Faltaba incrementar!
            return dir_temp

        # En caso de que haya otro tipo que no de error 
        self.contador_temp += 1
        temporal_name = f"t{self.contador_temp}"
        return temporal_name
    
    def registrar_variable(self, nombre, tipo):
        """Asigna una dirección de memoria virtual a una nueva variable y la guarda."""
        direccion = None
        
        # 1. Determinar el scope (¿Estamos dentro de una función o en el área global?)
        if self.funcion_en_construccion:
            # Scope LOCAL
            if tipo == "entero":
                direccion = self.contador_local_entero
                self.contador_local_entero += 1
            elif tipo == "flotante":
                direccion = self.contador_local_flotante
                self.contador_local_flotante += 1
            
            # Guardamos en la tabla de la función activa
            self.funcion_en_construccion["variables"][nombre] = {
                "tipo": tipo,
                "direccion": direccion
            }
        else:
            # Scope GLOBAL
            if tipo == "entero":
                direccion = self.contador_global_entero
                self.contador_global_entero += 1
            elif tipo == "flotante":
                direccion = self.contador_global_flotante
                self.contador_global_flotante += 1
                
            # Guardamos en la tabla global (índice 0)
            self.directorio_funciones[0]["variables"][nombre] = {
                "tipo": tipo,
                "direccion": direccion
            }
            
        return direccion

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
        # Determinar el tipo del operando y asignar/obtener dirección virtual
        if operando.lstrip('+-').isdigit():
            # 1. Constante entera
            if operando not in self.tabla_constantes:
                self.tabla_constantes[operando] = self.contador_constantes_enteras
                self.contador_constantes_enteras += 1
            
            dir_virtual = self.tabla_constantes[operando]
            self.pila_operandos.append(dir_virtual)  # Empujamos la dirección, NO el valor
            self.pila_tipos.append("entero")
            
        elif self._es_flotante(operando):
            # 2. Constante flotante
            if operando not in self.tabla_constantes:
                self.tabla_constantes[operando] = self.contador_constantes_flotantes
                self.contador_constantes_flotantes += 1
                
            dir_virtual = self.tabla_constantes[operando]
            self.pila_operandos.append(dir_virtual)  # Empujamos la dirección
            self.pila_tipos.append("flotante")
            
        else:
            # 3. Identificador — buscar en directorio
            tipo = self._buscar_tipo_variable(operando) # <-- Cambiado
            dir_virtual = self._buscar_direccion_variable(operando)
            
            self.pila_operandos.append(dir_virtual) 
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

    def _buscar_direccion_variable(self, nombre):
        """Busca una variable por nombre y retorna su dirección virtual."""
        # Buscar local primero
        if self.funcion_en_construccion:
            tabla_local = self.funcion_en_construccion.get("variables", {})
            if nombre in tabla_local:
                return tabla_local[nombre]["direccion"]

        # Buscar global
        tabla_global = self.directorio_funciones[0].get("variables", {})
        if nombre in tabla_global:
            return tabla_global[nombre]["direccion"]

        raise Exception(f"Error interno: Variable '{nombre}' no tiene dirección asignada.")

    def tipo_resultado(self, tipo1, operador, tipo2):
        resultado = self.cubo_semantico.get((tipo1, operador, tipo2))
        if resultado is None:
            raise Exception(f"Operación inválida: {tipo1} {operador} {tipo2}")
        return resultado
    
    def _buscar_tipo_variable(self, nombre):
        """Busca una variable por nombre y retorna su tipo."""
        # Buscar local primero
        if self.funcion_en_construccion:
            tabla_local = self.funcion_en_construccion.get("variables", {})
            if nombre in tabla_local:
                return tabla_local[nombre]["tipo"]

        # Buscar global
        tabla_global = self.directorio_funciones[0].get("variables", {})
        if nombre in tabla_global:
            return tabla_global[nombre]["tipo"]

        raise Exception(f"Error semántico: Variable '{nombre}' no declarada.")

    # ── operaciones ──────────────────────────────────────────────────────────

    def ejecutar_operacion(self):
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
        resultado = self.nuevo_temporal(tipo_res)

        # Emitir cuádruplo
        self.fila_cuadruplos.append(Cuadruplo(operador, operando1, operando2, resultado))

        # El temporal vuelve a la pila como operando para la siguiente operación
        self.pila_operandos.append(resultado)
        self.pila_tipos.append(tipo_res)

    def finalizar_expresion(self):
        """Procesa todos los operadores pendientes al final de una expresión"""
        while self.pila_operadores and self.pila_operadores[-1] != "=" and self.pila_operadores[-1] != "(":
            self.ejecutar_operacion()

    def obtener_cuadruplos(self):
        """Retorna la lista de cuádruplos generados"""
        return self.fila_cuadruplos