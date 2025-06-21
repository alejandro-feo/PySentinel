"""
Módulo interno que contiene la clase principal SecureAPIManager.
Esta es la implementación central de la lógica de gestión de claves.
"""

import base64
import logging
import subprocess
import sys
import re
from pathlib import Path

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    print("Error: Falta la dependencia 'cryptography'. Por favor, instálala.", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SecureAPIManager:
    """
    Gestiona claves API forzando la autenticación del sistema (vía sudo)
    en cada operación, verificando la configuración de huella en PAM, e invalidando
    la sesión de sudo después de cada uso para máxima seguridad.
    """
    def __init__(self, service_name: str, keys_dir: Path = None):
        """
        Inicializa el gestor y ejecuta la verificación de entorno de seguridad.
        """
        if not self._check_fingerprint_sudo_is_active():
            error_msg = (
                "ERROR DE SEGURIDAD: La autenticación por huella dactilar para sudo no está activada.\n"
                "Este programa requiere esta configuración para operar de forma segura."
            )
            raise RuntimeError(error_msg)

        if not service_name or not service_name.strip():
            raise ValueError("El nombre del servicio no puede estar vacío.")
        
        self.service_name = "".join(c for c in service_name if c.isalnum() or c in ('-', '_')).rstrip()
        
        if keys_dir is None:
            self.keys_dir = Path.home() / ".config" / "user_api_keys"
        else:
            self.keys_dir = Path(keys_dir)

        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.key_file_path = self.keys_dir / f"{self.service_name}.enc"

    def _check_fingerprint_sudo_is_active(self) -> bool:
        """
        Verifica si la autenticación por huella está en la config PAM para sudo,
        siguiendo las directivas @include para ser más robusto.
        """
        logging.info("Verificando la configuración de sudo para autenticación por huella...")
        
        pam_dir = Path("/etc/pam.d")
        files_to_check = [pam_dir / "sudo"]
        checked_files = set()
        fingerprint_module_found = False

        while files_to_check:
            current_file = files_to_check.pop(0)
            if current_file in checked_files or not current_file.exists():
                continue
            
            checked_files.add(current_file)
            logging.info(f"Inspeccionando archivo PAM: {current_file}")
            
            try:
                with open(current_file, 'r') as f:
                    for line in f:
                        clean_line = line.strip()
                        if clean_line.startswith('#') or not clean_line:
                            continue
                        if (sys.platform == "darwin" and "pam_tid.so" in clean_line) or \
                           (sys.platform.startswith("linux") and "pam_fprintd.so" in clean_line):
                            logging.info(f"Módulo de huella encontrado en {current_file}.")
                            fingerprint_module_found = True
                            break
                        match = re.match(r'@include\s+([\w-]+)', clean_line)
                        if match:
                            included_file = pam_dir / match.group(1)
                            if included_file not in checked_files:
                                files_to_check.append(included_file)
                if fingerprint_module_found:
                    break
            except Exception as e:
                logging.warning(f"No se pudo procesar el archivo PAM {current_file}: {e}")
                continue
        
        if not fingerprint_module_found:
            logging.error("Verificación fallida: No se encontró la configuración de huella en la cadena de archivos PAM para sudo.")
        return fingerprint_module_found
    
    def _get_master_encryption_key(self) -> bytes:
        """
        Obtiene la clave de cifrado maestra con sudo y LUEGO invalida la sesión de sudo.
        """
        logging.info("Solicitando clave de cifrado maestra. Requiere autenticación de superusuario.")
        try:
            # El script auxiliar es instalado en el mismo directorio que este módulo.
            helper_script_path = Path(__file__).parent / "get_master_key.py"
            if not helper_script_path.exists():
                raise FileNotFoundError("El script auxiliar 'get_master_key.py' no se encuentra.")

            result = subprocess.run(
                ['sudo', sys.executable, str(helper_script_path)],
                capture_output=True, text=True, check=True
            )
            
            master_key = result.stdout.strip()
            if not master_key:
                raise ValueError("La clave maestra obtenida a través de sudo está vacía.")
            
            logging.info("Clave de cifrado maestra obtenida con éxito.")
            return master_key.encode('utf-8')

        except FileNotFoundError as e:
            logging.error(f"Error de archivo: {e}")
            raise RuntimeError(f"No se pudo encontrar un archivo necesario. ¿Se ha realizado la configuración inicial?") from e
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip()
            logging.error(f"El script auxiliar falló: {error_message}")
            raise RuntimeError(f"Fallo al obtener la clave maestra. Razón: {error_message}") from e
        finally:
            # Este bloque se ejecuta SIEMPRE para invalidar el timestamp de sudo.
            logging.info("Invalidando la sesión de sudo para mayor seguridad.")
            subprocess.run(['sudo', '-k'], check=False)

    def set_api_key(self, api_key_value: str):
        """Cifra y almacena una nueva clave API tras autenticarse."""
        if not api_key_value:
            raise ValueError("La clave API a guardar no puede estar vacía.")
        master_key = self._get_master_encryption_key()
        fernet = Fernet(master_key)
        encrypted_api_key = fernet.encrypt(api_key_value.encode('utf-8'))
        with open(self.key_file_path, "wb") as f:
            f.write(encrypted_api_key)
        logging.info(f"Clave para '{self.service_name}' guardada de forma segura en {self.key_file_path}")

    def get_api_key(self) -> str:
        """Obtiene y descifra la clave API tras autenticarse."""
        if not self.key_file_path.exists():
            raise FileNotFoundError(f"No hay clave configurada para el servicio '{self.service_name}'.")
        master_key = self._get_master_encryption_key()
        with open(self.key_file_path, "rb") as f:
            encrypted_data = f.read()
        try:
            fernet = Fernet(master_key)
            decrypted_api_key = fernet.decrypt(encrypted_data)
            logging.info(f"Clave para '{self.service_name}' descifrada con éxito.")
            return decrypted_api_key.decode('utf-8')
        except InvalidToken:
            logging.error("Fallo al descifrar: token inválido. La clave maestra puede haber cambiado.")
            raise ValueError("No se pudo descifrar la clave API. El archivo podría estar corrupto o la clave maestra es incorrecta.")