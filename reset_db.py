import sqlite3

connection = sqlite3.connect('inventario.db')
cursor = connection.cursor()

# 1. Limpieza total
cursor.execute("DROP TABLE IF EXISTS entradas")
cursor.execute("DROP TABLE IF EXISTS salidas")
cursor.execute("DROP TABLE IF EXISTS productos")
cursor.execute("DROP TABLE IF EXISTS proveedores")

# 2. Tablas Base
cursor.execute("""
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    categoria TEXT,
    precio_compra REAL DEFAULT 0.0,
    precio_venta REAL DEFAULT 0.0,
    stock INTEGER DEFAULT 0,
    stock_min INTEGER DEFAULT 0,
    descripcion TEXT
)
""")

cursor.execute("""
CREATE TABLE proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ruc TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    telefono TEXT,
    direccion TEXT
)
""")

# 3. Tabla ENTRADAS (Con campo VENCIMIENTO)
cursor.execute("""
CREATE TABLE entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    proveedor_id INTEGER,
    cantidad INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    vencimiento TEXT,  -- Nuevo campo crítico
    usuario TEXT,
    motivo TEXT,
    FOREIGN KEY(producto_id) REFERENCES productos(id),
    FOREIGN KEY(proveedor_id) REFERENCES proveedores(id)
)
""")

cursor.execute("""
CREATE TABLE salidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    usuario TEXT,
    motivo TEXT,
    FOREIGN KEY(producto_id) REFERENCES productos(id)
)
""")

# Datos de prueba mínimos
cursor.execute("INSERT INTO proveedores (ruc, nombre, telefono, direccion) VALUES ('00000000000', 'Proveedor General', '000-000', 'Local')")

connection.commit()
connection.close()
print("LISTO: Base de datos actualizada con Control de Vencimientos.")