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
            "*": 2,
            "/": 2,
            "-": 1,
            "+": 1,
            ">": 0,
            "<": 0,
            "==": 0,
            "!=": 0,
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

    def ejecutar_operacion(self):
        """Genera un cuádruplo para la operación que está en la cima de la pila de operadores"""
        if not self.pila_operadores or len(self.pila_operandos) < 2:
            return
        
        operador = self.pila_operadores.pop()
        operando2 = self.pila_operandos.pop()
        operando1 = self.pila_operandos.pop()
        
        # Crear temporal para almacenar el resultado
        self.contador_temp += 1
        resultado = f"t{self.contador_temp}"
        
        # Crear y agregar el cuádruplo
        cuadruplo = Cuadruplo(operador, operando1, operando2, resultado)
        self.fila_cuadruplos.append(cuadruplo)
        
        # El resultado temporal se convierte en operando para la siguiente operación
        self.pila_operandos.append(resultado)

    def finalizar_expresion(self):
        """Procesa todos los operadores pendientes al final de una expresión"""
        while self.pila_operadores:
            self.ejecutar_operacion()

    def obtener_cuadruplos(self):
        """Retorna la lista de cuádruplos generados"""
        return self.fila_cuadruplos