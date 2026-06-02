class semanticContext:
    def __init__(self):
        # Pilas
        self.pila_operandos = []
        self.pila_operadores = []
        self.pila_tipos = []
        self.pila_saltos = []

        #Cuadruplos
        self.fila_cuadruplos = []
        self.contador_temp = 0

        self.directorio_funciones = []
        self.funcion_en_construccion = None

    def reset(self):
        self.pila_operandos.clear()
        self.pila_operadores.clear()
        self.pila_tipos.clear()
        self.pila_saltos.clear()
        self.fila_cuadruplos.clear()
        self.contador_temp = 0
        self.directorio_funciones.clear()
        self.funcion_en_construccion = None

    def nuevo_temporal(self):
        temporal_name = f"t{len(self.pila_operandos)}"
        self.pila_operandos.append(temporal_name)
        return temporal_name
    
    def precedencia(self, operador):
        precedencias = {
            "*" | "/" : 2,
            '-' | '+' : 1,
            ">" | "<" | "==" | "!=" : 0,
            '_' : -1  # Para operadores unarios como negación
        }
        return precedencias.get(operador, 0)
    
    # push

    def push_operando(self, operando):
        self.pila_operandos.append(operando)

    def push_operador(self, operador):
        while (self.pila_operadores and 
               self.precedencia(self.pila_operadores[-1]) >= self.precedencia(operador)):
            self.ejecutar_operacion()
        self.pila_operadores.append(operador)

    def push_tipo(self, tipo):
        self.pila_tipos.append(tipo)

    

