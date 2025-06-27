#!/bin/bash
#
# Script para desinstalar de forma segura el Gestor de Claves.
# Elimina los archivos de la aplicación y los enlaces simbólicos.

# --- Variables de Configuración ---
APP_NAME="sapiman"
INSTALL_DIR="/usr/local/lib/$APP_NAME"
BIN_DIR="/usr/local/bin"

function check_root() {
    # Asegura que el script se ejecute con privilegios de root.
    if [ "$(id -u)" -ne 0 ]; then
        echo "Error: Este script debe ejecutarse con sudo." >&2
        exit 1
    fi
}

# --- Script Principal ---
check_root

echo "Desinstalando el paquete $APP_NAME..."

# 1. Eliminar enlaces simbólicos
echo "Eliminando enlaces simbólicos..."
rm -f "$BIN_DIR/sapiman"
rm -f "$BIN_DIR/secure-app-example"

# 2. Eliminar directorio de la aplicación
echo "Eliminando directorio de instalación..."
rm -rf "$INSTALL_DIR"

echo "---------------------------------------------------------"
echo "NOTA IMPORTANTE:"
echo "La clave de cifrado maestra en /etc/secure_api_keys y las claves API cifradas"
echo "del usuario en ~/.config/user_api_keys NO han sido eliminadas por seguridad."
echo "Si deseas eliminarlas, debes hacerlo manualmente."
echo "---------------------------------------------------------"
echo "¡Desinstalación completada!"