from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .config import Config

# initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # register the blueprint
    from .routes import bp
    app.register_blueprint(bp)

    return app

# define the user_loader function
@login_manager.user_loader
def load_user(user_id):
    from .models import User  # import here to avoid circular dependency
    return User.query.get(int(user_id))