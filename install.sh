#!/bin/bash
# install.sh (Versión final que solo instala la librería y el CLI)

# Salir inmediatamente si un comando falla.
set -e

# --- Variables de Configuración ---
APP_NAME="sapiman"
LIB_INSTALL_DIR="/usr/local/lib/$APP_NAME"
BIN_DIR="/usr/local/bin"
MASTER_KEY_DIR="/etc/secure_api_keys"
MASTER_KEY_FILE="$MASTER_KEY_DIR/master.key"

# --- Funciones Auxiliares ---

function check_root() {
    # Asegura que el script se ejecute con privilegios de root.
    if [ "$(id -u)" -ne 0 ]; then
        echo "Error: Este script debe ejecutarse con privilegios de superusuario." >&2
        echo "Por favor, ejecútalo con: sudo ./install.sh" >&2
        exit 1
    fi
}

function check_dependencies() {
    # Verifica que las dependencias necesarias (python, pip, cryptography) estén disponibles.
    echo "Verificando dependencias del sistema..."
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 no está instalado." >&2
        exit 1
    fi
    if ! python3 -m pip &> /dev/null; then
        echo "Error: pip para python3 no está instalado." >&2
        exit 1
    fi
    if ! python3 -c "import cryptography" &> /dev/null; then
        echo "La dependencia 'cryptography' no está instalada. Intentando instalarla..."
        python3 -m pip install cryptography
        if [ $? -ne 0 ]; then
            echo "Error: No se pudo instalar 'cryptography'. Por favor, instálala manualmente." >&2
            exit 1
        fi
    fi
}


# --- Script Principal ---
#
# Primero, se definen las funciones y luego se llaman.
# La ejecución del script comienza aquí.

check_root
check_dependencies

echo "Iniciando la instalación de la librería $APP_NAME..."

# 1. Crear directorios de instalación y copiar el paquete.
echo "Copiando la librería a $LIB_INSTALL_DIR..."
rm -rf "$LIB_INSTALL_DIR"
mkdir -p "$LIB_INSTALL_DIR"
cp -r secure_module/* "$LIB_INSTALL_DIR/"
# COPIAMOS TAMBIÉN EL CLIENTE A LA LIBRERÍA, YA QUE ES PARTE DE ELLA
cp key_setter_client.py "$LIB_INSTALL_DIR/"

# 2. Generar el archivo de hashes de integridad.
echo "Generando archivo de hashes de integridad..."
HASHES_DB_FILE="$LIB_INSTALL_DIR/hashes.db"
echo "{" > "$HASHES_DB_FILE"
# Itera sobre los archivos .py del paquete para calcular su hash.
for py_file in $(find "$LIB_INSTALL_DIR" -name "*.py"); do
    filename=$(basename "$py_file")
    hash=$(sha256sum "$py_file" | awk '{ print $1 }')
    # Añade la entrada al archivo JSON.
    echo "  \"$filename\": \"$hash\"," >> "$HASHES_DB_FILE"
done
# Elimina la última coma para formar un JSON válido y cierra el objeto.
sed -i '$ s/,$//' "$HASHES_DB_FILE"
echo "}" >> "$HASHES_DB_FILE"

# 3. Establecer permisos y propiedad seguros.
echo "Estableciendo permisos de seguridad..."
chown -R root:root "$LIB_INSTALL_DIR"
chmod -R 555 "$LIB_INSTALL_DIR"
chmod 444 "$LIB_INSTALL_DIR/hashes.db"

# 4. Crear el enlace simbólico para la herramienta de CLI.
echo "Creando enlace simbólico para 'key-manager' en $BIN_DIR..."
ln -sf "$LIB_INSTALL_DIR/key_setter_client.py" "$BIN_DIR/key-manager"

# 5. Configurar la clave maestra si no existe.
if [ ! -f "$MASTER_KEY_FILE" ]; then
    echo "Configurando la clave de cifrado maestra..."
    mkdir -p "$MASTER_KEY_DIR"
    python3 -c "from cryptography.fernet import Fernet; key = Fernet.generate_key(); print(key.decode())" > "$MASTER_KEY_FILE"
    chown root:root "$MASTER_KEY_FILE"
    chmod 600 "$MASTER_KEY_FILE"
    echo "Clave maestra creada en $MASTER_KEY_FILE."
else
    echo "La clave maestra ya existe. Omitiendo creación."
fi

echo ""
echo "¡Instalación de la librería completada!"
echo "La herramienta 'key-manager' ya está disponible globalmente."
echo "Ahora puedes importar 'secure_module' en cualquiera de tus scripts de Python."
