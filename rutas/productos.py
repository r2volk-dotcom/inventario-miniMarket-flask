import sqlite3
from flask import Blueprint, render_template, request, jsonify
from models.db import get_db

# --- ¿QUÉ ES UN BLUEPRINT? ---
# Un Blueprint es como una "mini aplicación Flask" que agrupa rutas relacionadas.
# En vez de registrar rutas directamente en app, las registramos en el Blueprint.
# Luego app.py las importa y las une a la app principal con register_blueprint().
#
# Argumentos de Blueprint:
#   "productos"  → nombre interno (usado por url_for, debe ser único en todo el proyecto)
#   __name__     → le dice a Flask en qué módulo está (necesario para encontrar templates)
productos_bp = Blueprint("productos", __name__)


# --- PÁGINA PRINCIPAL ---
@productos_bp.route("/")
# @productos_bp.route en vez de @app.route → la ruta pertenece a este Blueprint
def index():
    conn = get_db()

    productos = conn.execute("SELECT * FROM productos ORDER BY nombre").fetchall()
    # fetchall() → devuelve TODOS los resultados como una lista de filas
    # ORDER BY nombre → los ordena alfabéticamente por nombre

    conn.close()
    # Siempre hay que cerrar la conexión para liberar la memoria del sistema

    return render_template("index.html", productos=productos)
    # render_template() busca el archivo en la carpeta /templates
    # productos=productos → pasa la lista al HTML para que pueda mostrarla con Jinja2


# --- AGREGAR PRODUCTO ---
@productos_bp.route("/add_product", methods=["POST"])
# methods=["POST"] → esta ruta SOLO acepta peticiones POST (no se puede visitar desde el navegador)
# El frontend la llama usando fetch() cuando se envía el formulario
def add_product():

    # request.form.get() lee los datos enviados en el formulario HTML
    # El segundo argumento es el valor por defecto si el campo no viene
    # .strip() elimina espacios al inicio y al final del texto
    codigo      = request.form.get("codigo", "").strip()
    nombre      = request.form.get("nombre", "").strip()
    categoria   = request.form.get("categoria", "General").strip()
    stock_min   = request.form.get("stock_min", "0").strip()
    descripcion = request.form.get("descripcion", "").strip()
    precio_compra = request.form.get("precio_compra", "0")
    precio_venta  = request.form.get("precio_venta", "0")

    # Validación de campos obligatorios
    # Si falta el código o el nombre, se devuelve un error antes de tocar la BD
    if not codigo or not nombre:
        return jsonify({"ok": False, "msg": "Código y nombre son obligatorios."}), 400
        # jsonify() convierte el dict Python en una respuesta JSON
        # 400 = código HTTP "Bad Request" (el cliente envió datos incorrectos)

    # Los datos del formulario llegan como strings → hay que convertirlos al tipo correcto
    try:
        stock_min     = int(stock_min)
        precio_compra = float(precio_compra)
        precio_venta  = float(precio_venta)
    except ValueError:
        # ValueError ocurre si intentas hacer int("abc") o float("--")
        return jsonify({"ok": False, "msg": "Valores numéricos inválidos."}), 400

    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO productos
              (codigo, nombre, categoria, precio_compra, precio_venta, stock, stock_min, descripcion)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?)
        """, (codigo, nombre, categoria, precio_compra, precio_venta, stock_min, descripcion))
        # Los ? son placeholders que SQLite reemplaza con los valores de la tupla
        # Esto PREVIENE inyección SQL → nunca concatenes strings del usuario directamente en SQL
        # El stock empieza en 0 porque no hay entradas registradas todavía

        conn.commit()
        # commit() guarda los cambios de forma permanente
        # Sin commit(), los cambios existen solo en memoria y se pierden al cerrar la conexión

        return jsonify({"ok": True, "msg": "Producto registrado."})

    except sqlite3.IntegrityError:
        # IntegrityError ocurre cuando se viola una restricción de la BD
        # En este caso: el código ya existe (tiene restricción UNIQUE en la tabla)
        return jsonify({"ok": False, "msg": "Código ya registrado."}), 400

    finally:
        conn.close()
        # finally se ejecuta SIEMPRE, haya error o no
        # Garantiza que la conexión se cierre incluso si ocurre una excepción
