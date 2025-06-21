#!/usr/bin/env python3
"""
Script auxiliar diseñado para ser ejecutado con sudo.

Su única función es leer la clave maestra de una ubicación protegida del sistema
y escribirla en la salida estándar para que el proceso padre (SecureAPIManager)
pueda capturarla. No debe ser ejecutado directamente por el usuario.
"""
import sys

MASTER_KEY_PATH = "/etc/secure_api_keys/master.key"

def main():
    """Lee la clave maestra y la imprime a stdout."""
    try:
        with open(MASTER_KEY_PATH, 'r') as f:
            master_key = f.read().strip()
        # Imprime la clave a stdout sin saltos de línea adicionales.
        print(master_key, end='')
    except FileNotFoundError:
        sys.stderr.write(f"ERROR: No se encuentra la clave maestra en {MASTER_KEY_PATH}.\n")
        sys.exit(1)
    except PermissionError:
        sys.stderr.write(f"ERROR: Permiso denegado para leer {MASTER_KEY_PATH}.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
