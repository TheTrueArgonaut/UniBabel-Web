# UniBabel - SRIMI Compliant Micro Main Entry Point
# S: Single Responsibility - App initialization only
# R: Reactive - Service injection for async operations  
# I: Injection - All dependencies injected
# M: Micro - Under 60 lines, focused
# I: Interfaces - Clear contracts

from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from models import db, User, create_tables
from routes import register_all_routes

def create_app() -> Flask:
    """Factory pattern for app creation - single responsibility"""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions with dependency injection
    db.init_app(app)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Store socketio in app context for injection
    app.extensions['socketio'] = socketio
    
    # Configure authentication
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register authentication blueprint
    from auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register admin authentication
    from admin_auth import admin_auth
    app.register_blueprint(admin_auth)
    
    # Register all micro routes
    register_all_routes(app)
    
    return app, socketio

def main():
    """Application entry point - micro and focused"""
    app, socketio = create_app()
    
    with app.app_context():
        create_tables()
    
    socketio.run(app, debug=True, port=5000, host='127.0.0.1')

if __name__ == '__main__':
    main()