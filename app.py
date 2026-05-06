from flask import Flask, session, redirect, url_for

# Importamos cada Blueprint desde su archivo correspondiente
# Un Blueprint es un grupo de rutas que se registra en la app principal
from rutas.auth        import auth_bp
from rutas.productos   import productos_bp
from rutas.movimientos import movimientos_bp
from rutas.proveedores import proveedores_bp
from rutas.api         import api_bp


#Factory Function...
def create_app():

    # __name__ le dice a Flask en qué módulo está corriendo
    # Flask lo usa para encontrar la carpeta /templates y /static
    app = Flask(__name__)

    # SECRET_KEY es necesaria para usar session (cookies firmadas)
    app.secret_key = "dj-minimarket-secret-2024"

    # --- REGISTRO DE BLUEPRINTS ---
    # register_blueprint() une las rutas del Blueprint a la app principal

    # Registra: GET /login, POST /login, GET /logout
    app.register_blueprint(auth_bp)

    # Registra: GET /  y  POST /add_product
    app.register_blueprint(productos_bp)

    # Registra: POST /add_entry, POST /add_output, GET /historial
    app.register_blueprint(movimientos_bp)

    # Registra: POST /add_provider
    app.register_blueprint(proveedores_bp)

    # Registra: GET /api/products, GET /api/providers, GET /api/dashboard
    app.register_blueprint(api_bp)

    # --- PROTECCIÓN DE RUTAS ---
    # Antes de cada request, verifica si hay sesión activa
    # Si no la hay, redirige al login (excepto para /login y /static)
    @app.before_request
    def require_login():
        from flask import request
        rutas_publicas = {"auth.login", "static"}
        # 👇 si pertenece al blueprint "api", no exigir login
        if request.blueprint == "api":
            return
        if not session.get("autenticado"):
            if request.endpoint not in rutas_publicas:
                return redirect(url_for("auth.login"))

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
