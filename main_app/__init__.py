import os
from flask import Flask
from flask_login import LoginManager
from main_app.database import migrate, db
from main_app.card import models
from main_app.auth import models

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile("config.py")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getcwd()}\\database.sqlite"
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from main_app.card.views import card

    app.register_blueprint(card)

    from main_app.auth.views import auth

    app.register_blueprint(auth)

    return app
