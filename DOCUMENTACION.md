# Sistema de Gestión de Inventario para Mini Market
### Documentación Técnica del Proyecto

**Repositorio:** https://github.com/rlaur205/inventario-colegio-flusk  
**Tecnología principal:** Python · Flask · SQLite · HTML/CSS/JavaScript 

---

## 1. Descripción General

El **Sistema de Gestión de Inventario para un Mini market** es una aplicación web desarrollada con el framework Flask (Python) que permite administrar el inventario de una tienda. El sistema registra productos, controla entradas y salidas de stock, gestiona proveedores y genera reportes visuales a través de un dashboard interactivo.

Este proyecto fue desarrollado como trabajo para un curso universitario y abarca los conceptos fundamentales de desarrollo web backend, manejo de bases de datos relacionales y construcción de APIs REST.

---

## 2. Estructura del Proyecto

```
inventario-colegio-flusk/
│
├── app.py               # Aplicación principal Flask (rutas y lógica)
├── reset_db.py          # Script para crear/reiniciar la base de datos
├── inventario.db        # Base de datos SQLite
│
├── templates/           # Plantillas HTML (Jinja2)
│   ├── index.html       # Página principal / Dashboard
│   └── historial.html   # Vista del historial de movimientos
│
└── static/              # Archivos estáticos
    ├── CSS              # Estilos de la interfaz
    └── JavaScript       # Lógica del lado del cliente (Chart.js, etc.)
```

---

## 3. Tecnologías Utilizadas

| Tecnología | Versión | Uso                                |
| ---------- | ------- | ---------------------------------- |
| Python     | 3.x     | Lenguaje de programación principal |
| Flask      | —       | Framework web backend              |
| SQLite     | —       | Base de datos relacional embebida  |
| HTML5      | —       | Estructura de las vistas           |
| CSS3       | —       | Estilos y diseño de la interfaz    |
| JavaScript | ES6+    | Interactividad del frontend        |
| Chart.js   | —       | Gráficos del dashboard             |

---

## 4. Base de Datos

El esquema de la base de datos es gestionado por el archivo `reset_db.py`. Contiene **4 tablas principales**:

### 4.1 Tabla `productos`
Almacena la información de cada producto del inventario.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER (PK) | Identificador único autoincremental |
| `codigo` | TEXT (UNIQUE) | Código único del producto |
| `nombre` | TEXT | Nombre del producto |
| `categoria` | TEXT | Categoría (ej: "General", "Limpieza", etc.) |
| `precio_compra` | REAL | Precio de adquisición |
| `precio_venta` | REAL | Precio de venta |
| `stock` | INTEGER | Cantidad actual en almacén |
| `stock_min` | INTEGER | Stock mínimo de alerta |
| `descripcion` | TEXT | Descripción opcional |

### 4.2 Tabla `proveedores`
Registra los datos de los proveedores.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER (PK) | Identificador único |
| `ruc` | TEXT (UNIQUE) | RUC del proveedor |
| `nombre` | TEXT | Nombre o razón social |
| `telefono` | TEXT | Número de contacto |
| `direccion` | TEXT | Dirección del proveedor |

### 4.3 Tabla `entradas`
Registra cada ingreso de mercancía al inventario.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER (PK) | Identificador único |
| `producto_id` | INTEGER (FK) | Referencia al producto |
| `proveedor_id` | INTEGER (FK) | Referencia al proveedor |
| `cantidad` | INTEGER | Unidades ingresadas |
| `fecha` | TEXT | Fecha y hora del ingreso |
| `vencimiento` | TEXT | Fecha de vencimiento del lote |
| `usuario` | TEXT | Responsable del registro |
| `motivo` | TEXT | Motivo del ingreso |

### 4.4 Tabla `salidas`
Registra cada salida o venta de productos.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER (PK) | Identificador único |
| `producto_id` | INTEGER (FK) | Referencia al producto |
| `cantidad` | INTEGER | Unidades retiradas |
| `fecha` | TEXT | Fecha y hora de la salida |
| `usuario` | TEXT | Responsable del registro |
| `motivo` | TEXT | Motivo de la salida |

---

## 5. Rutas de la Aplicación (API)

El archivo `app.py` define las siguientes rutas:

### 5.1 Vistas (HTML)

| Método | Ruta | Función | Descripción |
|---|---|---|---|
| GET | `/` | `index()` | Página principal con lista de productos |
| GET | `/historial` | `historial()` | Historial de movimientos (entradas + salidas) |

### 5.2 Acciones (POST)

| Método | Ruta | Función | Descripción |
|---|---|---|---|
| POST | `/add_product` | `add_product()` | Registra un nuevo producto |
| POST | `/add_entry` | `add_entry()` | Registra una entrada de stock |
| POST | `/add_output` | `add_output()` | Registra una salida/venta de stock |
| POST | `/add_provider` | `add_provider()` | Registra un nuevo proveedor |

### 5.3 Endpoints JSON (API REST)

| Método | Ruta | Función | Descripción |
|---|---|---|---|
| GET | `/api/products` | `api_products()` | Lista todos los productos (id, codigo, nombre, stock) |
| GET | `/api/providers` | `api_providers()` | Lista todos los proveedores (id, ruc, nombre) |
| GET | `/api/dashboard` | `api_dashboard()` | Estadísticas para el dashboard |

---

## 6. Detalle de Funciones Principales

### 6.1 `add_product()` — Agregar Producto
Registra un nuevo producto en la base de datos. Requiere `codigo` y `nombre` como campos obligatorios. Valida que los campos numéricos (`stock_min`, `precio_compra`, `precio_venta`) sean válidos y que el código no esté duplicado.

**Campos del formulario:**
- `codigo` *(obligatorio)*
- `nombre` *(obligatorio)*
- `categoria` (default: "General")
- `stock_min` (default: 0)
- `descripcion`
- `precio_compra`
- `precio_venta`

**Respuesta exitosa:** `{"ok": true, "msg": "Producto registrado."}`

---

### 6.2 `add_entry()` — Registrar Entrada de Stock
Registra el ingreso de unidades de un producto. Actualiza automáticamente el campo `stock` del producto sumando la cantidad ingresada. Incluye soporte para fecha de vencimiento del lote (por defecto `2099-12-31` si no se especifica).

**Campos del formulario:**
- `producto_id` *(obligatorio)*
- `proveedor_id` *(obligatorio)*
- `cantidad` *(obligatorio, debe ser > 0)*
- `vencimiento` (opcional)
- `usuario`
- `motivo`

---

### 6.3 `add_output()` — Registrar Salida/Venta
Registra la salida de unidades de un producto. Antes de proceder, **verifica que haya stock suficiente**. Si no hay stock suficiente, retorna un error descriptivo con la cantidad disponible. Descuenta automáticamente el stock del producto.

**Validación de stock:** Si `cantidad > stock_actual`, retorna:
```json
{"ok": false, "msg": "Stock insuficiente. Solo tienes X unidades de [producto]."}
```

---

### 6.4 `api_dashboard()` — Datos del Dashboard
Retorna un objeto JSON con los indicadores clave del inventario:

```json
{
  "total": 25,          // Total de productos registrados
  "alertas": 3,         // Productos con stock <= stock_min
  "vencimiento": 2,     // Lotes que vencen en los próximos 30 días
  "valor": 1500.50,     // Valor total del inventario (stock × precio_compra)
  "chart_labels": ["Limpieza", "Oficina"],
  "chart_values": [10, 15]
}
```

---

### 6.5 `historial()` — Historial de Movimientos
Combina las tablas `entradas` y `salidas` usando `UNION ALL` en SQL para mostrar un registro cronológico unificado de todos los movimientos del inventario, ordenado por fecha descendente.

**Query SQL utilizada:**
```sql
SELECT 'Entrada' as tipo, e.fecha, p.nombre as producto, e.cantidad, e.usuario, e.motivo
FROM entradas e JOIN productos p ON e.producto_id = p.id
UNION ALL
SELECT 'Salida' as tipo, s.fecha, p.nombre as producto, s.cantidad, s.usuario, s.motivo
FROM salidas s JOIN productos p ON s.producto_id = p.id
ORDER BY fecha DESC
```

---

## 7. Instalación y Ejecución

### Requisitos previos
- Python 3.x instalado
- pip (gestor de paquetes de Python)

### Pasos de instalación

**1. Clonar el repositorio:**
```bash
git clone https://github.com/rlaur205/inventario-colegio-flusk.git
cd inventario-colegio-flusk
```

**2. Instalar dependencias:**
```bash
pip install flask
```

**3. Inicializar la base de datos:**
```bash
python reset_db.py
```
> ⚠️ **Advertencia:** Este script elimina y recrea todas las tablas. Solo ejecutarlo la primera vez o cuando se desee reiniciar completamente los datos.

**4. Ejecutar la aplicación:**
```bash
python app.py
```

**5. Abrir en el navegador:**
```
http://localhost:5000
```

---

## 8. Funcionalidades del Sistema

- **Gestión de productos:** Registro con código único, categoría, precios de compra/venta, stock mínimo y descripción.
- **Control de entradas:** Registro de ingresos de mercancía por proveedor, con seguimiento de fechas de vencimiento por lote.
- **Control de salidas:** Registro de ventas o consumo interno con validación de stock disponible en tiempo real.
- **Gestión de proveedores:** Registro con RUC, nombre, teléfono y dirección.
- **Dashboard visual:** Indicadores de total de productos, alertas de stock bajo, productos próximos a vencer y valor total del inventario, con gráfico de distribución por categoría.
- **Historial completo:** Vista unificada y cronológica de todos los movimientos del inventario.
- **API REST:** Endpoints JSON para consumo dinámico desde el frontend.

---

## 9. Consideraciones Técnicas

- La conexión a la base de datos se maneja con la función auxiliar `get_db()`, que usa `sqlite3.Row` como `row_factory` para acceder a los campos por nombre de columna.
- Todas las respuestas de las rutas POST son en formato JSON (`{"ok": true/false, "msg": "..."}`) para facilitar el manejo de errores en el frontend sin recargar la página.
- Las fechas se almacenan en formato ISO 8601 (`YYYY-MM-DDTHH:MM:SS`).
- La aplicación corre en modo `debug=True` en el puerto `5000` durante el desarrollo. Para producción se debe deshabilitar el modo debug y configurar un servidor WSGI (como Gunicorn).

---

## 10. Posibles Mejoras Futuras

- Implementar un sistema de autenticación de usuarios con roles (administrador, operario).
- Agregar reportes exportables en PDF o Excel.
- Implementar paginación en el historial de movimientos.
- Separar la lógica de negocio en un archivo de servicios independiente del archivo de rutas.
- Migrar de SQLite a PostgreSQL para entornos de producción con mayor concurrencia.
- Agregar pruebas unitarias con `pytest`.

