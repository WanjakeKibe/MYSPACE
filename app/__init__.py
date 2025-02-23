from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = None


def create_app():
    app = Flask(__name__, template_folder='../templates',
                static_folder='../static')
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    global migrate
    migrate = Migrate(app, db)

    from .routes import main
    app.register_blueprint(main)

    return app
