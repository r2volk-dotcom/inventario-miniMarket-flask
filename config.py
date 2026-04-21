import os

# BASE_DIR apunta a la carpeta donde está este archivo (la raíz del proyecto)
# os.path.abspath asegura que sea una ruta absoluta, sin importar desde dónde se ejecute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construye la ruta completa al archivo de base de datos
# os.path.join une partes de una ruta de forma segura (funciona en Windows y Linux)
# Resultado ejemplo: "/home/usuario/proyecto/inventario.db"
DB_PATH = os.path.join(BASE_DIR, "inventario.db")
