"""
Módulo interno para la verificación de integridad de archivos.

Contiene la lógica para calcular hashes SHA256 de los archivos del paquete y
compararlos con una base de datos de hashes conocidos y buenos, generada
durante la instalación.
"""

import hashlib
from pathlib import Path
import json

def calculate_hash(file_path: Path) -> str:
    """Calcula y devuelve el hash SHA256 de un archivo dado."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # Lee el archivo en trozos para manejar eficientemente archivos de cualquier tamaño.
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def self_check():
    """
    Verifica la integridad de todos los archivos del paquete contra los hashes conocidos.

    Busca el archivo 'hashes.db' dentro del propio directorio del paquete.
    Compara el hash actual de cada archivo listado en la base de datos con su hash esperado.

    Raises:
        RuntimeError: Si el archivo 'hashes.db' no se encuentra, si un archivo del
                      paquete ha sido eliminado, o si el hash de un archivo no coincide,
                      indicando una posible modificación no autorizada.

    Returns:
        True si todas las verificaciones son exitosas.
    """
    package_dir = Path(__file__).parent
    hashes_db_path = package_dir / "hashes.db"

    if not hashes_db_path.exists():
        raise RuntimeError("FATAL: Archivo de hashes 'hashes.db' no encontrado. La aplicación no puede ejecutarse de forma segura.")

    with open(hashes_db_path, 'r') as f:
        known_hashes = json.load(f)

    for filename, expected_hash in known_hashes.items():
        file_to_check = package_dir / filename
        
        if not file_to_check.exists():
            raise RuntimeError(f"FATAL: ¡ALERTA DE SEGURIDAD! El archivo crítico '{filename}' ha sido eliminado.")

        current_hash = calculate_hash(file_to_check)
        
        if current_hash != expected_hash:
            raise RuntimeError(
                f"FATAL: ¡ALERTA DE SEGURIDAD! El archivo '{filename}' ha sido modificado o está corrupto.\n"
                "La ejecución ha sido abortada para proteger tus datos."
            )
            
    return True