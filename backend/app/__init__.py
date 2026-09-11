import os
from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, jwt, cors, socketio, redis_client
from app.middleware.error_handler import register_error_handlers
from app.websocket.handlers import register_websocket_handlers
from app.services.heartbeat_service import start_heartbeat_watchdog

def create_app(config_name=None):
    """Application factory for Employee Control Portal backend."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config.get("CORS_ORIGINS", "*"), supports_credentials=True)
    socketio.init_app(app, cors_allowed_origins="*", async_mode="threading")
    redis_client.init_app(app)

    # Register Error Handlers
    register_error_handlers(app)

    # Register WebSocket Handlers
    register_websocket_handlers(socketio)

    # Register Blueprints
    from app.modules.auth.routes import auth_bp
    from app.modules.dashboard.routes import dashboard_bp
    from app.modules.employees.routes import employees_bp
    from app.modules.departments.routes import departments_bp
    from app.modules.devices.routes import devices_bp
    from app.modules.agents.routes import agents_bp
    from app.modules.attendance.routes import attendance_bp
    from app.modules.sessions.routes import sessions_bp
    from app.modules.events.routes import events_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(events_bp)

    # Start Heartbeat Watchdog in non-testing environments
    if config_name != "testing" and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_heartbeat_watchdog(app, interval_seconds=10, timeout_seconds=60)

    @app.route("/health")
    def health_check():
        return {"status": "healthy", "service": "employee-control-portal-api", "version": "1.0.0"}

    return app
