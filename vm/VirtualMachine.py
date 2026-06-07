import json
import sys

from Memoria import Memoria

class VirtualMachine:
    def __init__(self, obj_file):
        # 1. Cargar el Código Objeto generado por el compilador
        with open(obj_file, 'r') as file:
            codigo_objeto = json.load(file)
            
        self.cuadruplos = codigo_objeto["cuadruplos"]
        self.directorio_funciones = codigo_objeto["directorio_funciones"]
        
        # 2. Inicializar la Memoria
        self.memoria = Memoria()
        
        # 3. Cargar las constantes en la memoria inmediatamente
        constantes = codigo_objeto["constantes"]
        for dir_virtual, valor_str in constantes.items():
            # Convertimos a int o float según corresponda para poder hacer matemáticas reales
            if '.' in valor_str:
                valor_real = float(valor_str)
            else:
                valor_real = int(valor_str)
            self.memoria.set_valor(dir_virtual, valor_real)
            
        # 4. Instruction Pointer (Apunta al cuádruplo actual)
        self.ip = 0

        # Pilas para el control de funciones
        self.pila_pendientes = [] # Prepara la memoria local antes de brincar
        self.pila_ejecucion = []  # Guarda a qué cuádruplo regresar después de la función

    def run(self):
        """El ciclo de vida de la Máquina Virtual."""
        print("--- INICIANDO EJECUCIÓN ---\n")
        
        total_cuadruplos = len(self.cuadruplos)
        
        while self.ip < total_cuadruplos:
            cuad = self.cuadruplos[self.ip]
            op = cuad["operador"]
            op1 = cuad["operando1"]
            op2 = cuad["operando2"]
            res = cuad["resultado"]
            
            # --- CEREBRO DE LA MÁQUINA VIRTUAL ---
            
            if op == "PRINT":
                valor = self.memoria.get_valor(op1)
                print(valor)
                self.ip += 1
                
            elif op == "=":
                # El valor a asignar está en op1, el destino está en res
                valor = self.memoria.get_valor(op1)
                self.memoria.set_valor(res, valor)
                self.ip += 1
                
            elif op in ["+", "-", "*", "/"]:
                # 1. Recuperar valores de la memoria
                val1 = self.memoria.get_valor(op1)
                val2 = self.memoria.get_valor(op2)
                
                # 2. Ejecutar operación de Python subyacente
                if op == "+":
                    resultado = val1 + val2
                elif op == "-":
                    resultado = val1 - val2
                elif op == "*":
                    resultado = val1 * val2
                elif op == "/":
                    resultado = val1 / val2
                    
                # 3. Guardar en la dirección destino
                self.memoria.set_valor(res, resultado)
                self.ip += 1
                
            elif op in [">", "<", "==", "!=", ">=", "<="]:
                val1 = self.memoria.get_valor(op1)
                val2 = self.memoria.get_valor(op2)
                
                if op == ">":
                    resultado = val1 > val2
                elif op == "<":
                    resultado = val1 < val2
                elif op == "==":
                    resultado = val1 == val2
                elif op == "!=":
                    resultado = val1 != val2
                    
                self.memoria.set_valor(res, resultado)
                self.ip += 1
                
            elif op == "GOTO":
                # Salto incondicional: actualizamos el IP directo al destino
                self.ip = int(res)
                
            elif op == "GOTOF":
                # Salto condicional: revisamos si el resultado booleano fue Falso
                condicion = self.memoria.get_valor(op1)
                
                if not condicion:  # Si la condición es False o 0
                    self.ip = int(res) # Brincamos
                else:
                    self.ip += 1       # Continuamos normal
            
            elif op == "ERA":
                # 1. Buscar la firma de la función
                func_info = next((f for f in self.directorio_funciones if f["nombre"] == op1), None)
                
                # 2. Crear una memoria temporal en la sala de espera
                self.pila_pendientes.append({
                    "nombre": op1,
                    "info": func_info,
                    "memoria": {}
                })
                self.ip += 1
                
            elif op == "PARAM":
                # 1. Obtener el valor que se quiere enviar
                valor = self.memoria.get_valor(op1)
                
                # 2. Saber qué número de parámetro es ("param0" -> 0)
                idx = int(res.replace("param", ""))
                
                # 3. Buscar la dirección virtual de ese parámetro en la tabla de la función
                pendiente = self.pila_pendientes[-1]
                nombre_param = pendiente["info"]["parametros"][idx]["nombre"]
                dir_param = pendiente["info"]["variables"][nombre_param]["direccion"]
                
                # 4. Guardar el valor en la sala de espera
                pendiente["memoria"][dir_param] = valor
                self.ip += 1
                
            elif op == "GOSUB":
                # 1. Activar la memoria local (Pasa de la sala de espera a la pila oficial)
                pendiente = self.pila_pendientes.pop()
                self.memoria.pila_locales.append(pendiente["memoria"])
                
                # 2. Guardar a dónde debemos regresar
                self.pila_ejecucion.append({
                    "ip_retorno": self.ip + 1,
                    "nombre_func": op1
                })
                
                # 3. Brincar a la función
                self.ip = int(res)
                
            elif op == "RETURN":
                # 1. Obtener el valor a retornar
                valor = self.memoria.get_valor(op1)
                
                # 2. Guardarlo en el buzón usando el nombre de la función actual
                nombre_func = self.pila_ejecucion[-1]["nombre_func"]
                self.memoria.set_valor(nombre_func, valor)
                self.ip += 1
                
            elif op == "ENDFUNC":
                # 1. Destruir la memoria local (Liberar RAM)
                self.memoria.pila_locales.pop()
                
                # 2. Recuperar el IP para regresar al flujo principal
                estado = self.pila_ejecucion.pop()
                self.ip = estado["ip_retorno"]
                    
            elif op == "END":
                break
                
            else:
                print(f"Operador '{op}' aún no implementado en la MV.")
                self.ip += 1

        print("\n--- EJECUCIÓN TERMINADA ---")