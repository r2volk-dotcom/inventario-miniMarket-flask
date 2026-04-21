import sqlite3
from flask import Blueprint, request, jsonify
from models.db import get_db

# Blueprint para todo lo relacionado con proveedores
proveedores_bp = Blueprint("proveedores", __name__)


# --- AGREGAR PROVEEDOR ---
@proveedores_bp.route("/add_provider", methods=["POST"])
def add_provider():

    # Leemos los campos del formulario
    # Si no vienen, usamos string vacío como valor por defecto
    ruc       = request.form.get("ruc", "").strip()
    nombre    = request.form.get("nombre", "").strip()
    telefono  = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()

    # RUC y nombre son obligatorios → si falta alguno, rechazamos la petición
    if not ruc or not nombre:
        return jsonify({"ok": False, "msg": "RUC y Nombre son obligatorios."}), 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO proveedores (ruc, nombre, telefono, direccion) VALUES (?, ?, ?, ?)",
            (ruc, nombre, telefono, direccion)
        )
        # Los ? previenen inyección SQL (nunca concatenes datos del usuario en el SQL)

        conn.commit()
        return jsonify({"ok": True, "msg": "Proveedor registrado."})

    except sqlite3.IntegrityError:
        # El RUC tiene restricción UNIQUE en la BD → no pueden existir dos iguales
        # Si ya existe, SQLite lanza IntegrityError
        return jsonify({"ok": False, "msg": "El RUC ya existe."}), 400

    finally:
        conn.close()
        # Se ejecuta siempre (con o sin error) → garantiza que la conexión se cierre
