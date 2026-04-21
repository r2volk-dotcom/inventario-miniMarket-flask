import datetime
from flask import Blueprint, render_template, request, jsonify
from models.db import get_db

# Blueprint para las rutas de entradas, salidas e historial
# Agrupa todo lo relacionado con el movimiento de stock
movimientos_bp = Blueprint("movimientos", __name__)


# --- AGREGAR ENTRADA (COMPRA / INGRESO DE STOCK) ---
@movimientos_bp.route("/add_entry", methods=["POST"])
def add_entry():

    # Leemos los datos del formulario
    producto_id  = request.form.get("producto_id")
    proveedor_id = request.form.get("proveedor_id")
    cantidad     = request.form.get("cantidad")
    vencimiento  = request.form.get("vencimiento")  # Puede venir vacío si no es perecedero
    usuario      = request.form.get("usuario", "").strip()
    motivo       = request.form.get("motivo", "").strip()

    # Convertimos los IDs y la cantidad a enteros
    try:
        producto_id  = int(producto_id)
        proveedor_id = int(proveedor_id)
        cantidad     = int(cantidad)
    except (TypeError, ValueError):
        # TypeError si el valor es None; ValueError si es texto no numérico
        return jsonify({"ok": False, "msg": "Datos inválidos."}), 400

    if cantidad <= 0:
        return jsonify({"ok": False, "msg": "Cantidad debe ser mayor a 0."}), 400

    # Si no se ingresó fecha de vencimiento, usamos una fecha muy lejana
    # Esto representa productos que no tienen fecha de caducidad
    if not vencimiento:
        vencimiento = "2099-12-31"

    fecha = datetime.datetime.now().isoformat(timespec='seconds')
    # datetime.now() → fecha y hora actual del servidor
    # .isoformat() → convierte a string en formato ISO 8601: "2025-04-20T14:30:00"
    # timespec='seconds' → corta los microsegundos (más legible en la BD)

    conn = get_db()
    try:
        # PASO 1: Registrar el movimiento en el historial de entradas
        conn.execute("""
            INSERT INTO entradas
              (producto_id, proveedor_id, cantidad, fecha, vencimiento, usuario, motivo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (producto_id, proveedor_id, cantidad, fecha, vencimiento, usuario, motivo))

        # PASO 2: Aumentar el stock del producto correspondiente
        conn.execute(
            "UPDATE productos SET stock = stock + ? WHERE id = ?",
            (cantidad, producto_id)
        )
        # stock = stock + ? → suma la cantidad al stock actual (no lo reemplaza)
        # WHERE id = ? → solo afecta al producto correcto

        # IMPORTANTE: Estas dos operaciones deberían estar en una transacción explícita
        # (BEGIN/ROLLBACK) para evitar que queden inconsistentes si algo falla entre medio.
        # Mejora pendiente para producción.

        conn.commit()
        return jsonify({"ok": True, "msg": "Entrada registrada."})

    except Exception as e:
        # Capturamos cualquier error inesperado y lo devolvemos como mensaje
        return jsonify({"ok": False, "msg": str(e)}), 500
        # 500 = Internal Server Error (algo falló en el servidor)

    finally:
        conn.close()


# --- AGREGAR SALIDA (VENTA / EGRESO DE STOCK) ---
@movimientos_bp.route("/add_output", methods=["POST"])
def add_output():

    producto_id = request.form.get("producto_id")
    cantidad    = request.form.get("cantidad")
    usuario     = request.form.get("usuario", "").strip()
    motivo      = request.form.get("motivo", "").strip()

    try:
        producto_id = int(producto_id)
        cantidad    = int(cantidad)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "msg": "Datos inválidos."}), 400

    if cantidad <= 0:
        return jsonify({"ok": False, "msg": "Cantidad debe ser mayor a 0."}), 400

    conn = get_db()
    try:
        # PASO 1: Verificar que el producto existe y tiene stock suficiente
        prod = conn.execute(
            "SELECT stock, nombre FROM productos WHERE id = ?",
            (producto_id,)
        ).fetchone()
        # fetchone() → devuelve solo la primera fila, o None si no encuentra nada

        if not prod:
            return jsonify({"ok": False, "msg": "Producto no encontrado."}), 404
            # 404 = Not Found

        stock_actual = prod['stock']
        # Accedemos por nombre de columna gracias a row_factory = sqlite3.Row

        if cantidad > stock_actual:
            return jsonify({
                "ok": False,
                "msg": f"Stock insuficiente. Solo tienes {stock_actual} unidades de {prod['nombre']}."
            }), 400
            # f"..." → f-string: permite insertar variables en el texto con {}

        # PASO 2: Registrar la salida en el historial
        fecha = datetime.datetime.now().isoformat(timespec='seconds')
        conn.execute(
            "INSERT INTO salidas (producto_id, cantidad, fecha, usuario, motivo) VALUES (?, ?, ?, ?, ?)",
            (producto_id, cantidad, fecha, usuario, motivo)
        )

        # PASO 3: Restar la cantidad vendida del stock
        conn.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ?",
            (cantidad, producto_id)
        )

        conn.commit()
        return jsonify({"ok": True, "msg": "Venta/Salida registrada correctamente."})

    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500

    finally:
        conn.close()


# --- PÁGINA DE HISTORIAL DE MOVIMIENTOS ---
@movimientos_bp.route("/historial")
def historial():
    conn = get_db()

    # UNION ALL combina los resultados de dos SELECT en una sola tabla
    # Primera parte: todas las entradas (compras/ingresos)
    # Segunda parte: todas las salidas (ventas/egresos)
    # Las columnas deben coincidir en orden y tipo entre ambas partes
    #
    # JOIN une dos tablas usando una columna en común:
    #   entradas e JOIN productos p ON e.producto_id = p.id
    #   → para cada entrada, trae el nombre del producto desde la tabla productos
    #   → así mostramos "Arroz" en vez de solo "3" (el id)
    #
    # ORDER BY fecha DESC → los más recientes aparecen primero
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

    movimientos = conn.execute(query).fetchall()
    conn.close()

    return render_template("historial.html", movimientos=movimientos)
    # Pasa la lista de movimientos al template para que los muestre en una tabla
