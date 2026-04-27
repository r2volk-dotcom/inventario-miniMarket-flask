import datetime
# Blueprint = para orgaizar el proyecto en partes
# Jsonify = convierte datos de python(diccionarios, listas) a JSON para apis
from flask import Blueprint, jsonify
from models.db import get_db

# Blueprint para todas las rutas de la API (devuelven JSON, no HTML)
# url_prefix="/api" → todas las rutas de este Blueprint tendrán /api al inicio automáticamente
# Ejemplo: @api_bp.route("/products") responde en /api/products
# Sin url_prefix tendríamos que escribir "/api/products" en cada ruta → más propenso a errores
api_bp = Blueprint("api", __name__, url_prefix="/api")


# --- LISTA DE PRODUCTOS ---
@api_bp.route("/products")
def api_products():
    conexion = get_db()

    productos = conexion.execute(
        "SELECT id, codigo, nombre, stock FROM productos ORDER BY nombre"
    ).fetchall()
    conexion.close()

    data = []
    for x in productos:
        # dict(x) convierte cada fila de SQLite (tipo Row) en diccionario de python.
        data.append(dict(x))

    # jsonify convierte la lista de diccionarios en JSON:
    return jsonify(data)


# --- LISTA DE PROVEEDORES ---
@api_bp.route("/providers")
def api_providers():
    conexion = get_db()
    provedores = conexion.execute(
        "SELECT id, ruc, nombre FROM proveedores ORDER BY nombre"
    ).fetchall()
    conexion.close()
    return jsonify([dict(x) for x in provedores])


# --- DATOS DEL DASHBOARD ---
# Devuelve estadísticas y datos para los gráficos del panel principal
@api_bp.route("/dashboard")
def api_dashboard():
    conn = get_db()

    # 1. Ejecuta la consulta: COUNT(*) devuelve una tabla de una sola celda.
    # 2. .fetchone(): Obtiene esa celda, pero Python la recibe como una tupla, ej: (15,)
    # 3. [0]: Extrae el número de la tupla para que 'total_productos' sea un entero (15) y no una lista (15,).
    total_productos = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]

    # Cuenta productos con stock en alerta (stock actual ≤ stock mínimo)
    alertas_stock = conn.execute(
        "SELECT COUNT(*) FROM productos WHERE stock <= stock_min"
    ).fetchone()[0]

    # Calcula el valor total del inventario: suma(precio_compra × stock) para cada producto
    valor_total = conn.execute(
        "SELECT SUM(stock * precio_compra) FROM productos"
    ).fetchone()[0]

    # Si no hay productos, SUM devuelve NULL,Lo convertimos a 0 para no causar errores.
    if valor_total is None:
        valor_total = 0

    # Fechas para filtrar los lotes a vencer (en los proximos 30 días)
    # .isoformat() convierte datetime a string: "2025-05-20"
    hoy    = datetime.date.today().isoformat() #fecha de hoy
    limite = (datetime.date.today() + datetime.timedelta(days=30)).isoformat() #intervalo de 30 dias


    # f-string seguro (fechas generadas internamente, no input de usuario)
    # Cuenta cuantos registros hay en la tabla entradas cuyo vencimiento este entro hoy y 30dias
    por_vencer = conn.execute(
        f"SELECT COUNT(*) FROM entradas WHERE vencimiento <= '{limite}' AND vencimiento >= '{hoy}'"
    ).fetchone()[0]

    # Datos para el gráfico de barras: devuelve (categoria, cantidad)
    chart_query = conn.execute(
        "SELECT categoria, COUNT(*) AS cantidad FROM productos GROUP BY categoria"
    ).fetchall()


    # Cierra la conexion de la bd
    conn.close()

    # Separamos etiquetas y valores en dos listas paralelas para el gráfico
    labels = [row['categoria'] for row in chart_query]  # ["Abarrotes", "Bebidas", ...]
    values = [row['cantidad']  for row in chart_query]  # [10, 5, ...]

    #jsonify lo convierte en json..
    # El frontend lee este JSON con fetch("/api/dashboard") y lo usa para actualizar el dashboard
    return jsonify({
        "total":        total_productos,
        "alertas":      alertas_stock,
        "vencimiento":  por_vencer,
        "valor":        valor_total,
        "chart_labels": labels,
        "chart_values": values
    })
