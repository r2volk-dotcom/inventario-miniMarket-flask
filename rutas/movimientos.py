import datetime
# Blueprint = para orgaizar el proyecto en partes
# render_template = para mostrar archivos HTML
# request = contiene la informacion de la peticion que hace el usuario
# Jsonify = convierte datos de python(diccionarios, listas) a JSON para apis
from flask import Blueprint, render_template, request, jsonify
from models.db import get_db

# Blueprint para las rutas de entradas, salidas e historial
# Agrupa todo lo relacionado con el movimiento de stock
movimientos_bp = Blueprint("movimientos", __name__)


# POST - agrega entrada (compra/ingreso stock)
@movimientos_bp.route("/add_entry", methods=["POST"])
def add_entry():

    # Leemos los datos del formulario
    # request.form.get() lee los datos enviados en el formulario HTML
    producto_id  = request.form.get("producto_id","") # (nombre del campo, valor por defecto)
    proveedor_id = request.form.get("proveedor_id","")
    cantidad     = request.form.get("cantidad","")
    vencimiento  = request.form.get("vencimiento")
    usuario      = request.form.get("usuario", "").strip()
    motivo       = request.form.get("motivo", "").strip()

    # Convertimos los IDs y la cantidad a enteros
    try:
        producto_id  = int(producto_id)
        proveedor_id = int(proveedor_id)
        cantidad     = int(cantidad)
    except ValueError:
        # ValueError si el valor es vacio("") o texto no numerico
        return jsonify({"ok": False, "msg": "Datos inválidos."}), 400

    if cantidad <= 0:
        return jsonify({"ok": False, "msg": "Cantidad debe ser mayor a 0."}), 400

    # Si no se ingreso fecha de vencimiento, usamos una fecha muy lejana (productos sin fecha de caducidad)
    if not vencimiento:
        vencimiento = "2099-12-31"

    # fecha y hora actual del servidor en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS), sin microsegundos
    fecha = datetime.datetime.now().isoformat(timespec='seconds')


    conexion = get_db()
    try:
        # 1. Registrar el movimiento en el historial de entradas
        conexion.execute("""
            INSERT INTO entradas
              (producto_id, proveedor_id, cantidad, fecha, vencimiento, usuario, motivo)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (producto_id, proveedor_id, cantidad, fecha, vencimiento, usuario, motivo)
        )

        # 2. Aumentar el stock del producto correspondiente
        conexion.execute(
            "UPDATE productos SET stock = stock + ? WHERE id = ?",
            (cantidad, producto_id)
        )

        # 3. Guardamos cambios
        conexion.commit()

        return jsonify({"ok": True,"msg": "Entrada registrada."})
    except Exception as e:
        # Capturamos cualquier error inesperado y lo devolvemos como mensaje
        return jsonify({"ok": False,"msg": str(e)}), 500
    finally:
        #Cerrarmos la conexion, pase lo que pase
        conexion.close()


# POST - agregar Salida (venta/egreso de stock)
@movimientos_bp.route("/add_output", methods=["POST"])
def add_output():

    producto_id = request.form.get("producto_id","")
    cantidad    = request.form.get("cantidad","")
    usuario     = request.form.get("usuario", "").strip()
    motivo      = request.form.get("motivo", "").strip()

    try:
        producto_id = int(producto_id)
        cantidad    = int(cantidad)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "msg": "Datos inválidos."}), 400

    if cantidad <= 0:
        return jsonify({"ok": False, "msg": "Cantidad debe ser mayor a 0."}), 400

    conexion = get_db()
    try:
        # PASO 1: Verificar que el producto existe y tiene stock suficiente
        producto = conexion.execute(
            "SELECT stock, nombre FROM productos WHERE id = ?",
            (producto_id,)
        ).fetchone() # fetchone() devuelve solo la primera fila, o None si no encuentra nada

        if not producto:
            return jsonify({"ok": False, "msg": "Producto no encontrado."}), 404


        # Accedemos por nombre de columna gracias a row_factory = sqlite3.Row
        stockActual = producto['stock']

        if cantidad > stockActual:
            return jsonify({
                "ok": False,
                "msg": f"Stock insuficiente. Solo tienes {stockActual} unidades de {producto['nombre']}."
            }), 400

        # PASO 2: Registrar la salida en el historial
        fecha = datetime.datetime.now().isoformat(timespec='seconds')
        conexion.execute(
            "INSERT INTO salidas (producto_id, cantidad, fecha, usuario, motivo) VALUES (?, ?, ?, ?, ?)",
            (producto_id, cantidad, fecha, usuario, motivo)
        )

        # PASO 3: Restar la cantidad vendida del stock
        conexion.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ?",
            (cantidad, producto_id)
        )

        conexion.commit()
        return jsonify({"ok": True, "msg": "Venta/Salida registrada correctamente."})

    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500
    finally:
        conexion.close()


# --- PÁGINA DE HISTORIAL DE MOVIMIENTOS ---
@movimientos_bp.route("/historial")
def historial():
    conexion = get_db()

    query = """
        SELECT 'Entrada' AS tipo, e.fecha, p.nombre AS producto, e.cantidad, e.usuario, e.motivo
        FROM entradas e
        JOIN productos p ON e.producto_id = p.id

        UNION ALL

        SELECT 'Salida' AS tipo, s.fecha, p.nombre AS producto, s.cantidad, s.usuario, s.motivo
        FROM salidas s
        JOIN productos p ON s.producto_id = p.id

        ORDER BY fecha DESC
    """

    movimientos = conexion.execute(query).fetchall()
    conexion.close()

    # Pasa la lista de movimientos al template para que los muestre en una tabla
    return render_template("historial.html", movimientos=movimientos)
