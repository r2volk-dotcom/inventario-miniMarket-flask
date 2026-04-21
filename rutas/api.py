import datetime
from flask import Blueprint, jsonify
from models.db import get_db

# Blueprint para todas las rutas de la API (devuelven JSON, no HTML)
# url_prefix="/api" → todas las rutas de este Blueprint tendrán /api al inicio automáticamente
# Ejemplo: @api_bp.route("/products") responde en /api/products
# Sin url_prefix tendríamos que escribir "/api/products" en cada ruta → más propenso a errores
api_bp = Blueprint("api", __name__, url_prefix="/api")


# --- LISTA DE PRODUCTOS ---
# Consumida por el JavaScript del frontend para llenar los <select> de los modales
@api_bp.route("/products")
def api_products():
    conn = get_db()

    productos = conn.execute(
        "SELECT id, codigo, nombre, stock FROM productos ORDER BY nombre"
    ).fetchall()
    conn.close()

    data = [dict(x) for x in productos]
    # [dict(x) for x in productos] es una list comprehension:
    # equivale a:
    #   data = []
    #   for x in productos:
    #       data.append(dict(x))
    #
    # dict(x) convierte cada fila de SQLite (tipo Row) en un dict Python normal
    # Necesario porque jsonify() no sabe cómo serializar objetos Row directamente

    return jsonify(data)
    # jsonify convierte la lista de dicts en JSON:
    # [{"id": 1, "codigo": "ARR01", "nombre": "Arroz", "stock": 50}, ...]


# --- LISTA DE PROVEEDORES ---
# Consumida por el JavaScript del frontend para llenar el <select> del modal de entrada
@api_bp.route("/providers")
def api_providers():
    conn = get_db()
    provs = conn.execute(
        "SELECT id, ruc, nombre FROM proveedores ORDER BY nombre"
    ).fetchall()
    conn.close()
    return jsonify([dict(x) for x in provs])


# --- DATOS DEL DASHBOARD ---
# Devuelve estadísticas y datos para los gráficos del panel principal
@api_bp.route("/dashboard")
def api_dashboard():
    conn = get_db()

    # Cuenta el total de productos registrados en la BD
    total_productos = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    # COUNT(*) → cuenta todas las filas de la tabla
    # fetchone() → devuelve la primera (y única) fila: (42,)
    # [0] → extrae el número de esa tupla: 42

    # Cuenta productos con stock en alerta (stock actual ≤ stock mínimo)
    alertas_stock = conn.execute(
        "SELECT COUNT(*) FROM productos WHERE stock <= stock_min"
    ).fetchone()[0]

    # Calcula el valor total del inventario: suma(precio_compra × stock) para cada producto
    valor_total = conn.execute(
        "SELECT SUM(stock * precio_compra) FROM productos"
    ).fetchone()[0]

    if valor_total is None:
        valor_total = 0
    # Si no hay productos, SUM devuelve NULL (None en Python)
    # Lo convertimos a 0 para no causar errores al mostrarlo

    # Fechas para filtrar lotes próximos a vencer (en los próximos 30 días)
    hoy    = datetime.date.today().isoformat()
    limite = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    # date.today() → fecha de hoy: 2025-04-20
    # timedelta(days=30) → un intervalo de 30 días
    # .isoformat() → convierte a string: "2025-05-20"

    # ⚠️ NOTA: Esta query usa f-string en vez de ? (placeholder)
    # Es aceptable porque las fechas las genera el SERVIDOR (no el usuario)
    # Pero en general, siempre preferí usar ? para prevenir inyección SQL
    # Versión segura sería: conn.execute("... WHERE vencimiento <= ? AND vencimiento >= ?", (limite, hoy))
    por_vencer = conn.execute(
        f"SELECT COUNT(*) FROM entradas WHERE vencimiento <= '{limite}' AND vencimiento >= '{hoy}'"
    ).fetchone()[0]

    # Datos para el gráfico de barras: cantidad de productos por categoría
    chart_query = conn.execute(
        "SELECT categoria, COUNT(*) AS cantidad FROM productos GROUP BY categoria"
    ).fetchall()
    # GROUP BY categoria → agrupa todas las filas que tengan la misma categoría
    # COUNT(*) → cuenta cuántos productos hay en cada grupo
    # Resultado ejemplo: [("Abarrotes", 10), ("Bebidas", 5), ("Lácteos", 3)]

    conn.close()

    # Separamos etiquetas y valores en dos listas paralelas para el gráfico
    labels = [row['categoria'] for row in chart_query]  # ["Abarrotes", "Bebidas", ...]
    values = [row['cantidad']  for row in chart_query]  # [10, 5, ...]

    return jsonify({
        "total":        total_productos,
        "alertas":      alertas_stock,
        "vencimiento":  por_vencer,
        "valor":        valor_total,
        "chart_labels": labels,
        "chart_values": values
    })
    # El frontend lee este JSON con fetch("/api/dashboard") y lo usa para
    # actualizar los números del dashboard y renderizar el gráfico
