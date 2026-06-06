import sys
from grammar import crear_gramática
from semantic_context import SemanticContext
import json

class Compilador:

    def __init__(self):
        self.semantic = SemanticContext()
        self.lenguaje_patito = crear_gramática(self.semantic)

    #def run_tests(self):
    #    from tests.test_aritmetica import test_generacion_cuadruplos
    #    run_tests()

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

    def exportar(self, filename="cuadruplos.txt"):
        """
        Exporta las constantes, el directorio de funciones y los cuádruplos a un archivo de texto.
        para facilitar su revisión y uso posterior.
        """

        # Verificar que exista la carpeta de salida
        import os
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        


        constantes = self.semantic.tabla_constantes
        funciones = self.semantic.directorio_funciones
        cuadruplos = self.semantic.obtener_cuadruplos()

        # Invertir la tabla de constantes para mostrar los valores en lugar de las direcciones
        constantes_invertidas = {v: k for k, v in constantes.items()}

        with open(os.path.join(output_dir, filename), 'w') as file:
            file.write("=== CONSTANTES ===\n")
            file.write(json.dumps(constantes_invertidas, indent=4))
            file.write("\n\n=== DIRECTORIO DE FUNCIONES ===\n")
            file.write(json.dumps(funciones, indent=4))
            file.write("\n\n=== CUÁDRUPLOS GENERADOS ===\n")
            for i, cuad in enumerate(cuadruplos):
                file.write(f"{i}: {cuad}\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    # Cargar archivo
    compilador = Compilador()
    compilador.cargar_archivo(sys.argv[1])
    compilador.imprimir_constantes()
    compilador.imprimir_directorio_funciones()
    compilador.imprimir_cuadruplos()
    compilador.exportar()


if __name__ == "__main__":
    main()