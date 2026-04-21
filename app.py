from flask import Flask

# Importamos cada Blueprint desde su archivo correspondiente
# Un Blueprint es un grupo de rutas que se registra en la app principal
from rutas.productos   import productos_bp
from rutas.movimientos import movimientos_bp
from rutas.proveedores import proveedores_bp
from rutas.api         import api_bp


def create_app():
    """
    Factory function: crea y configura la app Flask.

    Usar una función en vez de crear 'app' directamente a nivel global
    es una buena práctica porque:
      - Permite crear múltiples instancias (útil para tests)
      - Evita problemas de importación circular
      - Es el patrón recomendado en proyectos Flask medianos/grandes
    """

    app = Flask(__name__)
    # __name__ le dice a Flask en qué módulo está corriendo
    # Flask lo usa para encontrar la carpeta /templates y /static

    # --- REGISTRO DE BLUEPRINTS ---
    # register_blueprint() une las rutas del Blueprint a la app principal
    # A partir de aquí, Flask ya conoce y puede responder todas esas URLs
    app.register_blueprint(productos_bp)
    # Registra: GET /  y  POST /add_product

    app.register_blueprint(movimientos_bp)
    # Registra: POST /add_entry, POST /add_output, GET /historial

    app.register_blueprint(proveedores_bp)
    # Registra: POST /add_provider

    app.register_blueprint(api_bp)
    # Registra: GET /api/products, GET /api/providers, GET /api/dashboard
    # (el url_prefix="/api" ya está definido dentro del Blueprint)

    return app
    # Devolvemos la app lista para usarse


# --- PUNTO DE ENTRADA ---
# Este bloque solo se ejecuta cuando corres: python app.py
# Si otro archivo importa este módulo (ej: para tests), NO se ejecuta
if __name__ == "__main__":
    app = create_app()

    app.run(
        debug=True,   # Recarga automáticamente al guardar cambios + muestra errores detallados
        port=5000     # La app estará disponible en http://localhost:5000
    )
