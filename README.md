# 🔐 SAPIMan: Secure API Manager

![Versión de Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Plataformas](https://img.shields.io/badge/plataforma-Linux%20%7C%20macOS-lightgrey.svg)
![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)

**SAPIMan** es una librería de Python y una herramienta de línea de comandos para la gestión de credenciales con un nivel de seguridad extremo. Protege tus claves API con autenticación biométrica forzada y auto-verificación de integridad. Su arquitectura se basa en una **filosofía de Confianza Cero (Zero Trust)**.

---

## Filosofía y Propósito

Las librerías estándar como `keyring` son útiles, pero a menudo los almacenes de credenciales del sistema se desbloquean una vez al iniciar sesión y permanecen abiertos. Esto permite que cualquier proceso que se ejecute bajo tu usuario acceda a las claves sin una nueva autenticación.

**SAPIMan** resuelve este problema de raíz. En lugar de usar el `keyring`, basa toda su seguridad en el mecanismo de `sudo`, que se puede configurar para requerir una autenticación biométrica para cada acción, proporcionando un control de acceso granular e ineludible.

## Pilares de Seguridad

SAPIMan no es un simple gestor; es un sistema de seguridad con múltiples capas de defensa.

*   **🔍 Auto-Verificación de Integridad (Raíz de Confianza):** La librería se protege a sí misma. En el momento de la importación, verifica que ninguno de sus archivos haya sido modificado. Si detecta una alteración, la ejecución se detiene de inmediato.
*   **⚡ Autenticación Explícita e Ineludible:** Cada vez que se solicita una clave, se requiere una nueva autenticación biométrica a través de `sudo`. El módulo invalida la sesión de `sudo` (`sudo -k`) después de cada uso para eliminar cualquier período de gracia.
*   **✅ Verificación del Entorno (`Fail-Fast`):** El módulo comprueba activamente que tu sistema esté configurado para usar la huella dactilar con `sudo`. Si el entorno no cumple los requisitos de seguridad, la librería se negará a funcionar.
*   **🔐 Cifrado Robusto:** Las credenciales se cifran en reposo con `cryptography.fernet` (AES-128-CBC con HMAC), garantizando la confidencialidad e integridad de tus claves.

---

## ⚙️ Instalación y Configuración

El proceso está automatizado mediante un script que asegura una configuración correcta y segura.

### Paso 1: Configurar la Autenticación Biométrica para `sudo` (Requisito Indispensable)

#### Para Linux (Ubuntu, Debian, etc.)
1.  **Instalar software:**
    ```bash
    sudo apt-get update && sudo apt-get install fprintd libpam-fprintd
    ```
2.  **Registrar tu huella:**
    ```bash
    fprintd-enroll
    ```
3.  **Activar el módulo de autenticación (PAM):**
    ```bash
    sudo pam-auth-update
    ```
    En la interfaz que aparece, asegúrate de que la opción `Fingerprint authentication` esté seleccionada (`[*]`).

#### Para macOS (con Touch ID)
1.  Abre **Configuración del Sistema** → **Touch ID y contraseña**.
2.  Verifica que tienes una huella registrada y que la opción para **usar Touch ID con `sudo`** está activada.

### Paso 2: Ejecutar el Script de Instalación

1.  Clona o descarga este repositorio y navega hasta su directorio.
2.  Otorga permisos de ejecución al script:
    ```bash
    chmod +x install.sh
    ```
3.  Ejecuta el script con `sudo`:
    ```bash
    sudo ./install.sh
    ```
El script instalará la librería **SAPIMan**, la herramienta `sapiman`, y establecerá permisos de `root` para que no puedan ser modificados.

---

## 🚀 Uso

Una vez instalado, tienes dos formas de interactuar con el sistema:

### 1. Gestión de Claves con la Herramienta `sapiman`

Esta utilidad de línea de comandos está ahora disponible globalmente.

| Comando                               | Descripción                                            |
| ------------------------------------- | ------------------------------------------------------ |
| `sapiman --help`                      | Muestra el menú de ayuda.                              |
| `sapiman --add "nombre-de-mi-clave"`  | Añade o actualiza una credencial.                      |
| `sapiman --list`                      | Lista todas las credenciales guardadas.                |
| `sapiman --delete`                    | Inicia un menú interactivo para borrar una credencial. |
| `sapiman --delete-all`                | Borra **todas** las credenciales (con confirmación).   |

### 2. Integración en tus Propias Aplicaciones

Puedes crear un script de Python en **cualquier directorio** de tu sistema y usar la librería de forma segura.

```python
# /home/usuario/proyectos/mi_app.py
# Este script es un consumidor de la librería y puede estar en cualquier lugar.

import sys

# Añade la ruta de librerías del sistema para que Python encuentre 'sapiman'.
LIB_PATH = "/usr/local/lib"
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

try:
    # Esta importación es la puerta de entrada a la seguridad.
    # El paquete SAPIMan se autoverifica aquí. Si falla, el programa se detiene.
    from sapiman import SecureAPIManager

except (RuntimeError, ImportError) as e:
    print(f"Error fatal: No se pudo cargar la librería de seguridad.", file=sys.stderr)
    print(f"Razón: {e}", file=sys.stderr)
    sys.exit(1)


# --- Tu lógica de aplicación, completamente limpia ---

def main():
    nombre_clave = "api-key-de-mi-proyecto"
    print(f"Intentando obtener la credencial '{nombre_clave}'...")
    
    try:
        # Se instancia el gestor.
        manager = SecureAPIManager(service_name=nombre_clave)
        # Se solicita la clave. La autenticación biométrica ocurre aquí.
        api_key = manager.get_api_key()
        
        print(f"\n¡Éxito! Usando la clave que termina en '...{api_key[-4:]}'")
        # Aquí es donde usarías la clave:
        # mi_servicio_externo.conectar(api_key)

    except FileNotFoundError:
        print(f"\nError: La credencial '{nombre_clave}' no existe.", file=sys.stderr)
        print(f"Por favor, créala usando el comando: sapiman --add '{nombre_clave}'", file=sys.stderr)
    except Exception as e:
        print(f"\nHa ocurrido un error inesperado durante la operación: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
```

---

## 📦 Desinstalación

Para eliminar la librería y sus herramientas del sistema, navega al directorio original del proyecto y ejecuta:
```bash
chmod +x uninstall.sh
sudo ./uninstall.sh
```

> ⚠️ **Advertencia:** El script de desinstalación **no elimina** la clave maestra (`/etc/secure_api_keys/`) ni las credenciales de usuario cifradas (`~/.config/user_api_keys/`) por razones de seguridad. Debes borrarlas manualmente si así lo deseas.

---

## 📜 Licencia

Distribuido bajo la Licencia MIT.

---
