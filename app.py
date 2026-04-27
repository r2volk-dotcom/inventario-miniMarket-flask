from flask import Flask

# Importamos cada Blueprint desde su archivo correspondiente
# Un Blueprint es un grupo de rutas que se registra en la app principal
from rutas.productos   import productos_bp
from rutas.movimientos import movimientos_bp
from rutas.proveedores import proveedores_bp
from rutas.api         import api_bp


#Factory Function...
def create_app():

    # __name__ le dice a Flask en qué módulo está corriendo
    # Flask lo usa para encontrar la carpeta /templates y /static
    app = Flask(__name__)

    # --- REGISTRO DE BLUEPRINTS ---
    # register_blueprint() une las rutas del Blueprint a la app principal

    # Registra: GET /  y  POST /add_product
    app.register_blueprint(productos_bp)

    # Registra: POST /add_entry, POST /add_output, GET /historial
    app.register_blueprint(movimientos_bp)

    # Registra: POST /add_provider
    app.register_blueprint(proveedores_bp)

    # Registra: GET /api/products, GET /api/providers, GET /api/dashboard
    app.register_blueprint(api_bp)

    return app # Devolvemos la app lista para usarse


# --- PUNTO DE ENTRADA ---
# Este bloque solo se ejecuta cuando corres: python app.py
# Si otro archivo importa este módulo (ej: para tests), NO se ejecuta
if __name__ == "__main__":
    app = create_app()

    app.run(
        debug=True,   # Recarga automáticamente al guardar cambios + muestra errores detallados
        port=5000     # La app estará disponible en http://localhost:5000
    )
