#!/usr/bin/env python3
"""
Herramienta de línea de comandos para gestionar el ciclo de vida de las claves API.
Permite añadir, listar y eliminar claves de forma segura.
"""

import argparse
from getpass import getpass
import sys
from pathlib import Path

# La ruta donde el instalador colocó los módulos.
# Es necesario para que el script encuentre el paquete 'sapiman'.
INSTALL_DIR = "/usr/local/lib" 
sys.path.insert(0, INSTALL_DIR)

try:
    # La importación del paquete realiza la autoverificación de integridad.
    from sapiman import SecureAPIManager
except (RuntimeError, ImportError) as e:
    print(f"Error crítico al cargar el módulo de seguridad:", file=sys.stderr)
    print(f"{e}", file=sys.stderr)
    sys.exit(1)

# El directorio donde se guardan las claves cifradas del usuario.
KEYS_DIR = Path.home() / ".config" / "user_api_keys"

def get_stored_keys() -> list[Path]:
    """Escanea el directorio de claves y devuelve una lista ordenada de archivos .enc."""
    if not KEYS_DIR.exists():
        return []
    return sorted(list(KEYS_DIR.glob("*.enc")))

def list_keys():
    """Muestra una lista numerada de todas las claves guardadas."""
    print("--- Claves API Guardadas ---")
    stored_keys = get_stored_keys()
    if not stored_keys:
        print("No hay ninguna clave guardada.")
        return
    for i, key_file in enumerate(stored_keys, start=1):
        service_name = key_file.stem
        print(f"  {i}. {service_name}")

def add_key(service_name: str):
    """Añade o actualiza una clave para un servicio dado."""
    print(f"--- Añadiendo/Actualizando clave para: '{service_name}' ---")
    try:
        api_key_value = getpass("Por favor, introduce la nueva clave API (no se mostrará): ")
        if not api_key_value:
            print("\nError: La clave API no puede estar vacía.", file=sys.stderr)
            sys.exit(1)
        manager = SecureAPIManager(service_name=service_name, keys_dir=KEYS_DIR)
        manager.set_api_key(api_key_value)
        print(f"\n¡Éxito! La clave para '{service_name}' ha sido guardada.")
    except (RuntimeError, ValueError) as e:
        print(f"\nERROR durante el proceso: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.", file=sys.stderr)
        sys.exit(1)

def delete_interactive():
    """Muestra una lista de claves y permite al usuario borrar una por su número."""
    stored_keys = get_stored_keys()
    if not stored_keys:
        print("No hay claves para borrar.")
        return
    list_keys()
    print("-" * 28)
    try:
        choice_str = input("Introduce el número de la clave a borrar (o 0 para cancelar): ")
        choice = int(choice_str)
        if choice == 0:
            print("Operación cancelada.")
            return
        if not (1 <= choice <= len(stored_keys)):
            print("Error: Número fuera de rango.", file=sys.stderr)
            return
        key_to_delete = stored_keys[choice - 1]
        service_name = key_to_delete.stem
        confirm = input(f"¿Estás seguro de que quieres borrar la clave '{service_name}'? (s/n): ")
        if confirm.lower() == 's':
            key_to_delete.unlink()
            print(f"La clave '{service_name}' ha sido eliminada.")
        else:
            print("Borrado cancelado.")
    except ValueError:
        print("Error: Entrada no válida. Por favor, introduce un número.", file=sys.stderr)

def delete_all():
    """Borra TODAS las claves guardadas tras una confirmación estricta."""
    stored_keys = get_stored_keys()
    if not stored_keys:
        print("No hay claves para borrar.")
        return
    print("¡¡¡ADVERTENCIA!!! Esta acción borrará TODAS las claves guardadas.")
    confirm_phrase = "borrar todo"
    confirm_input = input(f'Para confirmar, escribe exactamente "{confirm_phrase}": ')
    if confirm_input == confirm_phrase:
        for key_file in stored_keys:
            key_file.unlink()
        print("Todas las claves han sido eliminadas.")
    else:
        print("Confirmación incorrecta. Operación cancelada.")

def main():
    parser = argparse.ArgumentParser(
        description="Cliente para gestionar claves API de forma segura.",
        epilog="Si no se especifica ninguna acción, se mostrará esta ayuda.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--add", metavar="SERVICE_NAME", help="Añade o actualiza una clave.")
    action_group.add_argument("-l", "--list", action="store_true", help="Muestra una lista de claves.")
    action_group.add_argument("-d", "--delete", action="store_true", help="Borra una clave de forma interactiva.")
    action_group.add_argument("--delete-all", action="store_true", help="Borra TODAS las claves guardadas.")
    args = parser.parse_args()
    action_provided = args.add or args.list or args.delete or args.delete_all
    if not action_provided:
        parser.print_help()
        sys.exit(0)
    if args.list:
        list_keys()
    elif args.add:
        add_key(service_name=args.add)
    elif args.delete:
        delete_interactive()
    elif args.delete_all:
        delete_all()

if __name__ == "__main__":
    main()
