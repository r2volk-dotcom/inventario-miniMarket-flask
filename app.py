from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3, os, datetime

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "inventario.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

@app.route("/")
def index():
    conn = get_db()
    # Ahora traemos tambien categoria y precios
    productos = conn.execute("SELECT * FROM productos ORDER BY nombre").fetchall()
    conn.close()
    return render_template("index.html", productos=productos)

@app.route("/add_product", methods=["POST"])
def add_product():
    codigo = request.form.get("codigo","").strip()
    nombre = request.form.get("nombre","").strip()
    categoria = request.form.get("categoria","General").strip()
    stock_min = request.form.get("stock_min","0").strip()
    descripcion = request.form.get("descripcion","").strip()
    
    # Nuevos campos de precios
    precio_compra = request.form.get("precio_compra","0")
    precio_venta = request.form.get("precio_venta","0")

    if not codigo or not nombre:
        return jsonify({"ok":False,"msg":"Código y nombre son obligatorios."}), 400
    
    try:
        stock_min = int(stock_min)
        precio_compra = float(precio_compra)
        precio_venta = float(precio_venta)
    except:
        return jsonify({"ok":False,"msg":"Valores numéricos inválidos."}), 400

    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO productos 
            (codigo, nombre, categoria, precio_compra, precio_venta, stock, stock_min, descripcion) 
            VALUES (?,?,?,?,?,0,?,?)
        """, (codigo, nombre, categoria, precio_compra, precio_venta, stock_min, descripcion))
        conn.commit()
        return jsonify({"ok":True,"msg":"Producto registrado."})
    except sqlite3.IntegrityError:
        return jsonify({"ok":False,"msg":"Código ya registrado."}), 400
    finally:
        conn.close()

@app.route("/add_entry", methods=["POST"])
def add_entry():
    producto_id = request.form.get("producto_id")
    proveedor_id = request.form.get("proveedor_id")
    cantidad = request.form.get("cantidad")
    vencimiento = request.form.get("vencimiento") # Nuevo
    usuario = request.form.get("usuario","").strip()
    motivo = request.form.get("motivo","").strip()
    
    try:
        producto_id = int(producto_id)
        proveedor_id = int(proveedor_id)
        cantidad = int(cantidad)
    except:
        return jsonify({"ok":False,"msg":"Datos inválidos."}), 400
        
    if cantidad <= 0:
        return jsonify({"ok":False,"msg":"Cantidad debe ser mayor a 0."}), 400
    
    # Validar fecha si viene vacía (ponemos una lejana por defecto si no es perecedero)
    if not vencimiento:
        vencimiento = "2099-12-31"

    fecha = datetime.datetime.now().isoformat(timespec='seconds')
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO entradas (producto_id, proveedor_id, cantidad, fecha, vencimiento, usuario, motivo) 
            VALUES (?,?,?,?,?,?,?)
        """, (producto_id, proveedor_id, cantidad, fecha, vencimiento, usuario, motivo))
        
        conn.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (cantidad, producto_id))
        conn.commit()
        return jsonify({"ok":True,"msg":"Entrada registrada."})
    except Exception as e:
        return jsonify({"ok":False,"msg":str(e)}), 500
    finally:
        conn.close()

@app.route("/api/products")
def api_products():
    conn = get_db()
    productos = conn.execute("SELECT id,codigo,nombre,stock FROM productos ORDER BY nombre").fetchall()
    conn.close()
    data = [dict(x) for x in productos]
    return jsonify(data)

@app.route("/add_output", methods=["POST"])
def add_output():
    producto_id = request.form.get("producto_id")
    cantidad = request.form.get("cantidad")
    usuario = request.form.get("usuario","").strip()
    motivo = request.form.get("motivo","").strip()
    
    try:
        producto_id = int(producto_id)
        cantidad = int(cantidad)
    except:
        return jsonify({"ok":False,"msg":"Datos inválidos."}), 400
        
    if cantidad <= 0:
        return jsonify({"ok":False,"msg":"Cantidad debe ser mayor a 0."}), 400

    conn = get_db()
    try:
        # 1. Verificar stock disponible antes de vender
        prod = conn.execute("SELECT stock, nombre FROM productos WHERE id = ?", (producto_id,)).fetchone()
        if not prod:
             return jsonify({"ok":False,"msg":"Producto no encontrado."}), 404
        
        stock_actual = prod['stock']
        if cantidad > stock_actual:
            return jsonify({"ok":False,"msg":f"Stock insuficiente. Solo tienes {stock_actual} unidades de {prod['nombre']}."}), 400

        # 2. Registrar la salida
        fecha = datetime.datetime.now().isoformat(timespec='seconds')
        conn.execute("INSERT INTO salidas (producto_id,cantidad,fecha,usuario,motivo) VALUES (?,?,?,?,?)",
                     (producto_id,cantidad,fecha,usuario,motivo))
        
        # 3. Restar el stock
        conn.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, producto_id))
        conn.commit()
        return jsonify({"ok":True,"msg":"Venta/Salida registrada correctamente."})
    except Exception as e:
        return jsonify({"ok":False,"msg":str(e)}), 500
    finally:
        conn.close()

@app.route("/add_provider", methods=["POST"])
def add_provider():
    ruc = request.form.get("ruc","").strip()
    nombre = request.form.get("nombre","").strip()
    telefono = request.form.get("telefono","").strip()
    direccion = request.form.get("direccion","").strip()

    if not ruc or not nombre:
        return jsonify({"ok":False,"msg":"RUC y Nombre son obligatorios."}), 400

    conn = get_db()
    try:
        conn.execute("INSERT INTO proveedores (ruc, nombre, telefono, direccion) VALUES (?,?,?,?)",
                     (ruc, nombre, telefono, direccion))
        conn.commit()
        return jsonify({"ok":True,"msg":"Proveedor registrado."})
    except sqlite3.IntegrityError:
        return jsonify({"ok":False,"msg":"El RUC ya existe."}), 400
    finally:
        conn.close()

@app.route("/api/providers")
def api_providers():
    conn = get_db()
    provs = conn.execute("SELECT id, ruc, nombre FROM proveedores ORDER BY nombre").fetchall()
    conn.close()
    return jsonify([dict(x) for x in provs])

@app.route("/api/dashboard")
def api_dashboard():
    conn = get_db()
    
    total_productos = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    alertas_stock = conn.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_min").fetchone()[0]
    valor_total = conn.execute("SELECT SUM(stock * precio_compra) FROM productos").fetchone()[0]
    if valor_total is None: valor_total = 0

    # Lógica de Vencimiento: Contar lotes que vencen en los próximos 30 días
    hoy = datetime.date.today().isoformat()
    limite = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    
    # Buscamos en 'entradas' aquellos lotes cuya fecha de vencimiento esté entre hoy y 30 días
    # (Asumiendo que aún hay stock, simplificado contamos lotes ingresados recientes)
    por_vencer = conn.execute(f"SELECT COUNT(*) FROM entradas WHERE vencimiento <= '{limite}' AND vencimiento >= '{hoy}'").fetchone()[0]

    chart_query = conn.execute("SELECT categoria, COUNT(*) as cantidad FROM productos GROUP BY categoria").fetchall()
    conn.close()
    
    labels = [row['categoria'] for row in chart_query]
    values = [row['cantidad'] for row in chart_query]

    return jsonify({
        "total": total_productos,
        "alertas": alertas_stock,
        "vencimiento": por_vencer, # Nuevo dato
        "valor": valor_total,
        "chart_labels": labels,
        "chart_values": values
    })

@app.route("/historial")
def historial():
    conn = get_db()
    # Usamos UNION ALL para combinar entradas y salidas en una sola lista
    query = """
        SELECT 'Entrada' as tipo, e.fecha, p.nombre as producto, e.cantidad, e.usuario, e.motivo 
        FROM entradas e
        JOIN productos p ON e.producto_id = p.id
        UNION ALL
        SELECT 'Salida' as tipo, s.fecha, p.nombre as producto, s.cantidad, s.usuario, s.motivo 
        FROM salidas s
        JOIN productos p ON s.producto_id = p.id
        ORDER BY fecha DESC
    """
    movimientos = conn.execute(query).fetchall()
    conn.close()
    return render_template("historial.html", movimientos=movimientos)

if __name__ == "__main__":
    app.run(debug=True, port=5000)