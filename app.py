import os
import random
from datetime import datetime
from time import sleep
from flask import Flask, render_template, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from tools.save_image import save_image
from tools.translate import translate
from tools.parse_yaml import list_files, parse_yaml


"""App init and config"""
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getcwd()}\\database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate()
migrate.init_app(app, db)

"""Models"""
class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {'sqlite_autoincrement': True}     # remove if postgres
    id = db.Column(db.Integer, primary_key=True)


class Card(BaseModel):
    __tablename__ = 'card'
    
    original_word = db.Column(db.String(128), unique=True, nullable=False)
    translated_word = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    vote_yes = db.Column(db.Integer, nullable=True)
    vote_no = db.Column(db.Integer, nullable=True)

    def __repr__(self) -> str:
        return f'<Card>: "{self.original_word}, {self.translated_word}"'

    @classmethod
    def list_add(cls, words: list, category_name: str) -> bool:
        custom_translate = None 
        if len(words) < 1:
            raise Exception('Length of list with words must me more than 1.')

        category = Category.get_or_create(category_name)
        for word in words:
            if ':' in word:
                word, custom_translate = word.split(':')[0], word.split(':')[1]
            card = db.session.query(Card).filter(Card.original_word==word).first()
            if card is None:
                if custom_translate:
                    translated_word = custom_translate
                else:
                    translated_word = translate(word)

                card = Card(original_word=word, translated_word=translated_word)
                sleep(0.5)
                try:
                    db.session.add(card)
                    db.session.commit()
                    category_and_card = CategoryCards(category_id=category.id, card_id=card.id)
                    db.session.add(category_and_card)
                    db.session.commit()
                except:
                    db.session.rollback()
                    print('Not added, ', card)
            else:
                category_and_card = db.session.query(CategoryCards).filter(CategoryCards.card_id==card.id, CategoryCards.category_id==category.id).first()
                if category_and_card is None:
                    category_and_card = CategoryCards(category_id=category.id, card_id=card.id)
                    db.session.add(category_and_card)
                    db.session.commit()
        return True

    def get_related_categories(self):
        related_categories = list()
        category_and_card = db.session.query(CategoryCards).filter(CategoryCards.card_id==self.id).all()
        for elem in category_and_card:
            category = db.session.query(Category).get(elem.category_id)
            related_categories.append(category)
        return related_categories


class Category(BaseModel):
    __tablename__ = 'category'
    name = db.Column(db.String(128), unique=True, nullable=False)
    image = db.Column(db.String(1024), nullable=True)
    background = db.Column(db.String(1024), nullable=True)

    def __repr__(self):
        return f'<Category> "{self.name}"'

    @classmethod
    def get_or_create(cls, category_name: str):
        try:
            category = db.session.query(Category).filter(Category.name == category_name).one()
            return category
        except:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()
            return category

    @classmethod
    def all(cls) -> list:
        categories = db.session.query(Category).all()
        return categories

    @property
    def count_words(self) -> int:
        count_words = db.session.query(CategoryCards).filter(CategoryCards.category_id==self.id).count()
        return count_words

    def get_first_card_id(self) -> int:
        category_card = db.session.query(CategoryCards).filter(CategoryCards.category_id==self.id).order_by(CategoryCards.category_id).first()
        return category_card.card_id


class CategoryCards(BaseModel):
    __tablename__ = 'categories_cards'
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    # category = db.relationship('Category')
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    # card = db.relationship('Card')


"""Views"""
@app.route('/')
def index():
    categories = Category.all()
    return render_template('main/index.html', categories=categories)


@app.route('/card/random')
def random_word():
    card = db.session.query(Card).order_by(func.random()).first()
    return render_template('main/card_random.html', card=card)


@app.route('/category/<int:category_id>')
def category(category_id):
    category = db.session.query(Category).get(category_id)
    return render_template('main/category.html', category=category)


@app.route('/category/<int:category_id>/<int:page>')
def category_words(category_id, page=1):
    exam = request.args.get('exam', 0, int)
    per_page = 1
    cards = list()
    category_cards = db.session.query(CategoryCards).filter(CategoryCards.category_id==category_id).order_by(CategoryCards.category_id).all()

    for category_card in category_cards:
        cards.append(category_card.card_id)
    
    paginate_cards = db.session.query(Card).filter(Card.id.in_(cards)).order_by(Card.id).paginate(page, per_page)
    template_name = 'main/cards.html'
    if exam == 2:
        template_name = 'main/cards_ru_sr.html'
    return render_template(template_name, cards=paginate_cards, category_id=category_id, exam=exam)


@app.route('/card/vote', methods=['POST'])
def card_vote():
    card_id = request.form.get('card_id', 0, int)
    vote = request.form.get('vote')
    card = db.session.query(Card).get(card_id)
    
    response = dict()
    if vote == 'true':
        if card.vote_yes:
            card.vote_yes += 1
            response = card.vote_yes
        else:
            card.vote_yes = 1
            response = card.vote_yes
    elif vote == 'false':
        if card.vote_no:
            card.vote_no += 1
            response = card.vote_no
        else:
            card.vote_no = 1
            response = card.vote_no
    else:
        raise ValueError('Bad vote')
    
    db.session.commit()
    return jsonify({'card_id':card.id, 'result': response}), 200


"""Debug routes"""
@app.route('/parse_yaml')
def card_parse_yaml():
    app_directory = os.path.join(os.getcwd(), 'dictionary')
    yaml_dicts = list_files(app_directory)
    results = list()
    for filename in yaml_dicts:
        file = os.path.join(app_directory, filename)
        dictionary = parse_yaml(file)
        category_name = list(dictionary.keys())[0]
        result = Card.list_add(dictionary[category_name], category_name)
        results.append({file: result})
    return jsonify(results)


@app.route('/templates/<name>')
def get_template(name):
    return render_template(f'html/{name}.html')


if __name__ == '__main__':
    app.run()
