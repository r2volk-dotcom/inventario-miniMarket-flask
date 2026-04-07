# 📦 Sistema de Gestión de Inventario para Minimarket

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Una solución web moderna diseñada para el control de suministros en tiendas pequeñas. Gestiona stock, proveedores y movimientos con reportes visuales en tiempo real.

---

## 🚀 Vista Previa del Sistema

### 📊 Dashboard e Indicadores
Visualiza el valor total de tu almacén, alertas de stock bajo y distribución por categorías.
![Dashboard](imgs/img7.png)

### 📋 Gestión de Inventario y Kardex
Control centralizado de productos y registro detallado de todas las operaciones (Entradas y Salidas).

| Vista de Inventario | Historial Completo (Kardex) |
| :---: | :---: |
| ![Inventario](imgs/img5.png) | ![Historial](imgs/img6.png) |

---

## 📸 Módulos de Registro
El sistema utiliza ventanas modales para agilizar la entrada de datos sin perder el contexto.

### ➕ Gestión de Stock (Entradas y Salidas)
| Registro de Entradas | Registro de Salidas |
| :---: | :---: |
| ![Entrada](imgs/img3.png) | ![Salida](imgs/img4.png) |

### 📝 Catálogos (Productos y Proveedores)
| Nuevo Producto | Nuevo Proveedor |
| :---: | :---: |
| ![Producto](imgs/img1.png) | ![Proveedor](imgs/img2.png) |

---

## ✨ Características Principales

* **Gestión de Stock Inteligente:** Validación de existencias en tiempo real para evitar errores en salidas.
* **Control de Vencimientos:** Seguimiento de lotes con fechas críticas para productos perecederos.
* **Dashboard Interactivo:** Gráficos dinámicos mediante **Chart.js**.
* **Historial Unificado:** Registro cronológico de cada movimiento con responsable y motivo.
* **Arquitectura Eficiente:** Backend en Flask con persistencia de datos en SQLite.

---

## 🛠️ Stack Tecnológico

* **Backend:** Python & Flask
* **Base de Datos:** SQLite 3
* **Frontend:** HTML5, CSS3, JavaScript (ES6+)
* **Gráficos:** Chart.js

---
## ⚙️ Instalación y Ejecución

1. **Clona el repositorio:**
   `git clone https://github.com/rlaur205/inventario-colegio-flusk.git`
   `cd inventario-colegio-flusk`

2. **Instala las dependencias:**
   `pip install flask`

3. **Inicializa la base de datos:**
   `python reset_db.py`

4. **Lanza la aplicación:**
   `python app.py`

5. **Accede en tu navegador a:**
   `http://localhost:5000`
