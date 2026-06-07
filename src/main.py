import sys
from grammar import crear_gramática
from semantic_context import SemanticContext
import json
import os

class Compilador:

    def __init__(self):
        self.semantic = SemanticContext()
        self.lenguaje_patito = crear_gramática(self.semantic)

    def cargar_archivo(self, filename="programa.patito"):
        try:
            with open(filename, 'r') as file:
                content = file.read()

                if not content.strip():
                    print(f"Error: El archivo '{filename}' está vacío.")
                    return
                
                # Validar sintaxis y realizar análisis semántico
                try:
                    self.lenguaje_patito.parse_string(content)
                    print("Archivo cargado y validado correctamente.")
                except Exception as e:
                    print(f"Error de sintaxis: {e}")
                    return

        except FileNotFoundError:
            print(f"Error: El archivo '{filename}' no se encontró.")
        except Exception as e:
            print(f"Error al cargar el archivo: {e}")

    def imprimir_constantes(self):
        ce = self.semantic.tabla_constantes
        print ("\n=== CONSTANTES ===")
        print(json.dumps(ce, indent=4))

    def imprimir_directorio_funciones(self):    
        df = self.semantic.directorio_funciones
        print ("\n=== DIRECTORIO DE FUNCIONES ===")
        print(json.dumps(df, indent=4))
    
    def imprimir_cuadruplos(self):
        cuadruplos = self.semantic.obtener_cuadruplos()
        if cuadruplos:
            print("\n=== CUÁDRUPLOS GENERADOS ===")
            for i, cuad in enumerate(cuadruplos):
                print(f"{i}: {cuad}")
        else:
            print("\nNo se generaron cuádruplos.")

    def exportar(self, filename="programa.obj"):
        """
        Empaqueta las constantes, el directorio de funciones y los cuádruplos 
        en un solo archivo JSON (Código Objeto) para la Máquina Virtual.
        """
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 1. Invertir constantes (La MV necesita buscar por dirección, ej: { "9000": "3.14" })
        constantes = self.semantic.tabla_constantes
        constantes_invertidas = {v: k for k, v in constantes.items()}

        # 2. Directorio de Funciones
        funciones = self.semantic.directorio_funciones

        # 3. Serializar Cuádruplos a diccionarios
        cuadruplos_serializados = []
        for cuad in self.semantic.obtener_cuadruplos():
            cuadruplos_serializados.append({
                "operador": cuad.operador,
                "operando1": cuad.operando1,
                "operando2": cuad.operando2,
                "resultado": cuad.resultado
            })

        # 4. Crear el Objeto Principal
        codigo_objeto = {
            "constantes": constantes_invertidas,
            "directorio_funciones": funciones,
            "cuadruplos": cuadruplos_serializados
        }

        # 5. Escribir el archivo JSON
        ruta_archivo = os.path.join(output_dir, filename)
        with open(ruta_archivo, 'w') as file:
            json.dump(codigo_objeto, file, indent=4)
            
        print(f"\n¡Código Objeto exportado con éxito a '{ruta_archivo}'!")


def main():
    if len(sys.argv) != 2:
        print("Usage: python compilador.py <filename>")
        sys.exit(1)

    # Cargar archivo
    compilador = Compilador()
    compilador.cargar_archivo(sys.argv[1])
    #compilador.imprimir_constantes()
    #compilador.imprimir_directorio_funciones()
    #compilador.imprimir_cuadruplos()
    compilador.exportar()

if __name__ == "__main__":
    main()