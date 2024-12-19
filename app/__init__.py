from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object('app.config.Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Define the login view
    login_manager.login_view = 'auth.login'  # Redirect unauthenticated users to the login page

    # Define the user loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User  # Import inside the function to avoid circular import
        return User.query.get(int(user_id))


    from app.routes import main as main_blueprint
    from app.admin import admin as admin_blueprint
    from app.auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(auth_blueprint)

    return app
