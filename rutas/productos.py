import sqlite3
from flask import Blueprint, render_template, request, jsonify
from models.db import get_db

productos_bp = Blueprint("productos", __name__)

# --- PAGINA PRINCIPAL ---
@productos_bp.route("/")
def index():
    conn = get_db()

    # fetchall() - devuelve TODOS los resultados como una lista de filas
    productos = conn.execute("SELECT * FROM productos ORDER BY nombre").fetchall()

    conn.close() # cerramos la conexion

    # render_template() busca el archivo en la carpeta /templates
    # productos=productos → pasa la lista al HTML para que pueda mostrarla con Jinja2
    return render_template("index.html", productos=productos)


# POST - agregar producto
@productos_bp.route("/add_product", methods=["POST"])
def add_product():

    # Leemos los datos del formulario
    # request.form.get() lee los datos enviados en el formulario HTML
    codigo      = request.form.get("codigo", "").strip()
    nombre      = request.form.get("nombre", "").strip()
    categoria   = request.form.get("categoria", "General").strip()
    stock_min   = request.form.get("stock_min", "0").strip()
    descripcion = request.form.get("descripcion", "").strip()
    precio_compra = request.form.get("precio_compra", "0")
    precio_venta  = request.form.get("precio_venta", "0")

    # Si falta el código o el nombre, se devuelve un error antes de tocar la BD
    if not codigo or not nombre:
        return jsonify({"ok": False, "msg": "Código y nombre son obligatorios."}), 400

    # Los datos del formulario llegan como strings, hay que convertirlos al tipo correcto
    try:
        stock_min     = int(stock_min)
        precio_compra = float(precio_compra)
        precio_venta  = float(precio_venta)
    except ValueError:
        return jsonify({"ok": False, "msg": "Valores numéricos inválidos."}), 400

    conexion = get_db()
    try:
        conexion.execute("""
            INSERT INTO productos
              (codigo, nombre, categoria, precio_compra, precio_venta, stock, stock_min, descripcion)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?)
        """, (codigo, nombre, categoria, precio_compra, precio_venta, stock_min, descripcion))
        # Los ? son placeholders que SQLite reemplaza con los valores de la tupla en ese orden

        # guardamos los cambios
        conexion.commit()

        return jsonify({"ok": True, "msg": "Producto registrado."})

    except sqlite3.IntegrityError:
        # IntegrityError ocurre cuando se viola una restricción de la BD
        # En este caso: el código ya existe (tiene restricción UNIQUE en la tabla)
        return jsonify({"ok": False, "msg": "Código ya registrado."}), 400

    finally:
        conexion.close()
