import os
from flask import Blueprint, render_template, request, jsonify
from main_app.card.models import Card, Category, CategoryCards

from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from main_app.tools.save_image import save_image
from main_app.tools.translate import translate
from main_app.tools.parse_yaml import list_files, parse_yaml
from main_app import db


card = Blueprint('card', __name__, template_folder='templates')


@card.route('/')
def index():
    categories = Category.all()
    return render_template('main/index.html', categories=categories)


@card.route('/random')
def random_word():
    card = db.session.query(Card).order_by(func.random()).first()
    return render_template('main/card_random.html', card=card)


@card.route('/category/<int:category_id>')
def category(category_id):
    category = db.session.query(Category).get(category_id)
    return render_template('main/category.html', category=category)


@card.route('/category/<int:category_id>/<int:page>')
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


@card.route('/vote', methods=['POST'])
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

@card.route('/parse_yaml')
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