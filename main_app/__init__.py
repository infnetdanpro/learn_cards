import os
from flask import Flask
from main_app.database import migrate, db
from main_app.card import models


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getcwd()}\\database.sqlite'
    db.init_app(app)
    migrate.init_app(app, db)

    from main_app.card.views import card
    app.register_blueprint(card)

    return app
