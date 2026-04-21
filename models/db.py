import sqlite3

# Importamos DB_PATH desde config.py para no repetir la ruta en cada archivo
from config import DB_PATH


def get_db():
    """
    Abre y devuelve una conexión a la base de datos SQLite.
    Se llama al inicio de cada ruta que necesite acceder a la BD.
    """

    conn = sqlite3.connect(DB_PATH)
    # sqlite3.connect() abre el archivo .db (lo crea si no existe)

    conn.row_factory = sqlite3.Row
    # row_factory cambia el formato de los resultados:
    # Sin esto:  row[0], row[1]  → acceso por índice numérico (confuso)
    # Con esto:  row['nombre'], row['stock']  → acceso por nombre de columna (legible)

    return conn
    # Devolvemos la conexión para que la ruta pueda ejecutar consultas
