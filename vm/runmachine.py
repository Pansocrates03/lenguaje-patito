import json
import sys

from VirtualMachine import VirtualMachine


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python virtual_machine.py <archivo.obj>")
        sys.exit(1)

    vm = VirtualMachine(sys.argv[1])
    vm.run()