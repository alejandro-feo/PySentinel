#!/usr/bin/env python3
"""
Aplicación de ejemplo que demuestra el uso del paquete sapiman.
"""
import sys

# La ruta donde el instalador colocó los módulos.
INSTALL_DIR = "/usr/local/lib" 
sys.path.insert(0, INSTALL_DIR)

try:
    # La importación del paquete realiza la autoverificación de integridad.
    # Si hay un problema de seguridad, la importación fallará con un error.
    from sapiman import SecureAPIManager
except (RuntimeError, ImportError) as e:
    print(f"Error crítico al cargar el módulo de seguridad:", file=sys.stderr)
    print(f"{e}", file=sys.stderr)
    sys.exit(1)

def main():
    """
    Función principal que demuestra cómo obtener una clave de forma segura.
    """
    print("Módulo de seguridad cargado y verificado con éxito.")
    print("Este script es un ejemplo. Usa 'sapiman' para gestionar claves.")
    
    key_name = input("Introduce el nombre de la clave que quieres obtener: ")
    if not key_name:
        return
        
    try:
        # Instanciar el gestor y obtener la clave.
        # La autenticación por huella se solicitará aquí.
        manager = SecureAPIManager(service_name=key_name)
        api_key = manager.get_api_key()
        print(f"\nÉxito. Clave obtenida: '...{api_key[-4:]}'")
        # Aquí se usaría la clave, por ejemplo:
        # service_client.authenticate(api_key)
    except Exception as e:
        print(f"\nError durante la operación: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
