import sys
from grammar import crear_gramática
from semantic_context import SemanticContext

class Compilador:

    def __init__(self):
        self.semantic = SemanticContext()
        self.lenguaje_patito = crear_gramática(self.semantic)

    def run_tests(self):
        from tests.test_aritmetica import run_tests
        run_tests()

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
    
    def imprimir_cuadruplos(self):
        cuadruplos = self.semantic.obtener_cuadruplos()
        if cuadruplos:
            print("\n=== CUÁDRUPLOS GENERADOS ===")
            for i, cuad in enumerate(cuadruplos):
                print(f"{i}: {cuad}")
        else:
            print("\nNo se generaron cuádruplos.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    # Cargar archivo
    compilador = Compilador()
    compilador.cargar_archivo(sys.argv[1])
    compilador.imprimir_cuadruplos()


if __name__ == "__main__":
    main()