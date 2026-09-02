from flask import Flask

from .config import Config
from .db import close_db, init_db
from .routes import api
from .sessions import EncryptedSessionInterface


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.session_interface = EncryptedSessionInterface(
        app.config["SECRET_ENCRYPTION_KEY"]
    )
    app.teardown_appcontext(close_db)
    app.register_blueprint(api)

    with app.app_context():
        init_db()

    return app
