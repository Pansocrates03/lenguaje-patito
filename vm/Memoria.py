class Memoria:
    def __init__(self):
        self.globales = {}
        self.temporales = {}
        self.constantes = {}
        self.pila_locales = []
        
        # NUEVO: Buzón especial para guardar los retornos de las funciones
        self.retornos = {} 

    def set_valor(self, direccion, valor):
        dir_str = str(direccion)
        
        # Si la dirección es un texto puro, va a los retornos
        if not dir_str.lstrip('-').isdigit():
            self.retornos[dir_str] = valor
            return
            
        dir_int = int(direccion)
        
        if 1000 <= dir_int < 3000:
            self.globales[dir_int] = valor
        elif 3000 <= dir_int < 5000:
            self.pila_locales[-1][dir_int] = valor
        elif 5000 <= dir_int < 8000:

            if len(self.pila_locales) > 0:
                # Si estamos dentro de una función, el temporal es de su contexto
                self.pila_locales[-1][dir_int] = valor
            else:
                # Si estamos en el programa principal, usamos la memoria temporal global
                self.temporales[dir_int] = valor
        elif 8000 <= dir_int < 10000:
            self.constantes[dir_int] = valor
        else:
            raise Exception(f"Error de Memoria: Dirección {dir_int} fuera de rango.")

    def get_valor(self, direccion):
        if direccion == "_":
            return None
            
        dir_str = str(direccion)
        
        # Si es un texto puro, buscar en el buzón de retornos
        if not dir_str.lstrip('-').isdigit():
            return self.retornos.get(dir_str, None)
            
        dir_int = int(direccion)
        
        if 1000 <= dir_int < 3000:
            return self.globales.get(dir_int, None)
        elif 3000 <= dir_int < 5000:
            return self.pila_locales[-1].get(dir_int, None)
        elif 5000 <= dir_int < 8000:
            # --- MISMA LÓGICA PARA RECUPERAR DATOS ---
            if len(self.pila_locales) > 0:
                return self.pila_locales[-1].get(dir_int, None)
            else:
                return self.temporales.get(dir_int, None)
        elif 8000 <= dir_int < 10000:
            return self.constantes.get(dir_int, None)
        else:
            raise Exception(f"Error de Memoria: Dirección {dir_int} fuera de rango.")