"""
Inicializa el paquete sapiman.

Este archivo actúa como un guardián de seguridad. Su principal responsabilidad es
ejecutar una autocomprobación de integridad de todos los archivos del paquete
antes de exponer la API pública (la clase SecureAPIManager).

Si la verificación falla por cualquier motivo (archivo modificado, corrupto o
eliminado), se lanzará una excepción RuntimeError, deteniendo la importación
y la ejecución de cualquier programa que dependa de este módulo.
"""

# 1. Importa y ejecuta la función de autoverificación del módulo interno.
#    Este paso es bloqueante y crítico para la seguridad.
from . import _verifier
_verifier.self_check()

# 2. Si la verificación fue exitosa, la ejecución continúa y se expone la API.
#    Esta línea solo se alcanza si la autocomprobación no lanzó excepciones.
from ._manager import SecureAPIManager

# Define la API pública del paquete para importaciones como 'from sapiman import *'.
__all__ = ['SecureAPIManager']