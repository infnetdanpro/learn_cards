import os
import itertools
import random

from sqlalchemy import func, text, desc, asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.inspection import inspect

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_required

from main_app import db
from main_app.card.models import Card, Category, CategoryCards, CardStats
from main_app.auth.models import UserSeed
from main_app.tools import save_image, translate, list_files, parse_yaml


card = Blueprint('card', __name__, template_folder='templates')


@card.route('/')
def index():
    categories = Category.all()
    return render_template('main/index.html', categories=categories)


@card.route('/random')
def random_word():
    card = db.session.query(Card).order_by(func.random()).first()
    return render_template('main/card/card_random.html', card=card)


@card.route('/category/<int:category_id>')
def category(category_id):
    if request.args.get('finish'):
        finish = True if request.args.get('finish') == 'True' else False
        result = UserSeed.create_new_seed(current_user)
        return redirect(url_for('card.category', category_id=category_id))
    
    category = db.session.query(Category).get(category_id)
    return render_template('main/card/category.html', category=category)


@card.route('/category/<int:category_id>/<int:page>')
def category_words(category_id, page=1):
    seed = UserSeed.get_by_user(current_user)
    exam = request.args.get('exam', 0, int)
    per_page = 1
    # only for postgres example
    # category_cards = db.session.query(CategoryCards).filter(CategoryCards.category_id==category_id).filter(text(f'setseed({seed})')).order_by(func.random()).all()

    category_cards = db.session.query(CategoryCards) \
                    .filter(CategoryCards.category_id==category_id) \
                    .order_by(CategoryCards.id) \
                    .all()
    cards = [category_card.card_id for category_card in category_cards]
    
    # only for sqlite. For postgres use setseed in DB!
    # Random ordering by column
    columns = [column.name for column in inspect(Card).columns]
    random_pairs = list(itertools.product(columns, [desc, asc]))
    random.seed(seed)
    column, ordering = random.choice(random_pairs)

    paginate_cards = db.session.query(Card).filter(Card.id.in_(cards)).order_by(ordering(text(f'Card.{column}'))).paginate(page, per_page)
    template_name = 'main/card/cards.html'
    if exam == 2:
        template_name = 'main/card/cards_ru_sr.html'
    return render_template(template_name, cards=paginate_cards, category_id=category_id, exam=exam)


def vote_handle(param_vote: str) -> tuple:
    if param_vote == 'true':
        param_vote = 1
    elif param_vote == 'false':
        param_vote = -1
    else:
        raise ValueError("Can't detect your vote!")
    return param_vote


@card.route('/vote', methods=['POST'])
@login_required
def card_vote():
    card_id = request.form.get('card_id', 0, int)
    card = db.session.query(Card).get(card_id)
    vote = vote_handle(request.form.get('vote'))
    
    response = dict(card_id=card.id)
    
    try:
        card_stat = db.session.query(CardStats) \
                                .filter(CardStats.card_id==card.id, CardStats.user_id==current_user.id) \
                                .one()
        if vote is not card_stat.vote:
            card_stat.vote = vote
            db.session.commit()
        else:
            return '', 200
    except NoResultFound:
        card_stat = CardStats(card=card, vote=vote, user=current_user)
        db.session.add(card_stat)
        db.session.commit()
    likes_positive, likes_negative = CardStats.get_stats(card_id=card.id)
    response['result'] = dict(positive=likes_positive, negative=likes_negative)
    return jsonify(response), 200


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