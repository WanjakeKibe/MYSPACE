from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

db = SQLAlchemy()
migrate = None


def create_app():
    app = Flask(__name__, template_folder='../templates',
                static_folder='../static')
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    @app.before_request
    def session_management():
        if 'user_id' in session:
            now = datetime.datetime.utcnow().timestamp()
            last_activity = session.get('last_activity', now)
            if now - last_activity > 600:  # 10 minutes
                session.pop('user_id', None)  # Logout user
            else:
                session['last_activity'] = now

    db.init_app(app)

    global migrate
    migrate = Migrate(app, db)

    from .routes import main, admin
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/api/admin')

    return app
