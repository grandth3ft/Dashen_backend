"""
Dashen Surveys - Flask API entry point.

Uses the application factory pattern so the app can be configured
differently for testing vs. development vs. production without
duplicating setup code.
"""

from flask import Flask, jsonify
from config import Config
from extensions import db, bcrypt, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    # FRONTEND_ORIGIN may be a single URL or a comma-separated list
    # (useful for allowing both a Vercel production domain and preview URLs).
    allowed_origins = [o.strip() for o in app.config["FRONTEND_ORIGIN"].split(",") if o.strip()]
    cors.init_app(app, resources={r"/*": {"origins": allowed_origins}})

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.survey_routes import survey_bp
    from routes.wallet_routes import wallet_bp
    from routes.withdrawal_routes import withdrawal_bp
    from routes.upgrade_routes import upgrade_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(withdrawal_bp)
    app.register_blueprint(upgrade_bp)
    app.register_blueprint(admin_bp)

    # Create tables and seed the default admin account on startup.
    # Both are idempotent, so this is safe to run every time the app boots.
    with app.app_context():
        import models  # noqa: F401 - ensures all models are registered before create_all()
        db.create_all()

        from utils.migrate import run_migrations
        run_migrations()

        from utils.seed import seed_admin
        seed_admin()

        from utils.seed_surveys import seed_surveys
        seed_surveys()

    @app.route("/")
    def health_check():
        return jsonify({"status": "ok", "service": "Dashen Surveys API"})

    return app


# Module-level app object -- required so a production WSGI server
# (e.g. `gunicorn app:app` on Render) can import it directly. Only
# app.run() should be gated behind __main__, not app creation itself.
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
