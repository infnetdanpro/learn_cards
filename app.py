from datetime import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

"""App init and config"""
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getcwd()}\\database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


"""Models"""
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_word = db.Column(db.String(128), nullable=False)
    translated_word = db.Column(db.String(128), nullable=False)
    image_word = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)

    def __repr__(self):
        return '<Card>: "%s"' % self.original_word


"""Views"""
@app.route('/')
def index():
    words = db.session.query(Card).filter(Card.active == True).all()
    return render_template('main/index.html', words=words)

# TODO: change to put method
# test: http://127.0.0.1:5000/add/card?original_word=%D0%BC%D0%B0%D1%88%D0%B8%D0%BD%D0%B0&translated_word=kola&image_word=https://i.imgur.com/KkAfQv7.jpg
@app.route('/add/card', methods=['GET'])
def add():
    if request.args:
        original_word = request.args.get('original_word')
        translated_word = request.args.get('translated_word')
        image_word = request.args.get('image_word')
    else:
        return 'Request args is required', 401
    card = Card(original_word=original_word, translated_word=translated_word, image_word=image_word)
    db.session.add(card)
    db.session.commit()

    return 'Ok'


if __name__ == '__main__':
    app.run()
