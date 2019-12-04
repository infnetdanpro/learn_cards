from main_app.database import db
from datetime import datetime
from time import sleep

from sqlalchemy import func, text
from main_app.tools.translate import translate


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

    def vote_yes(self, user_id):
        return CardStats.get_positive_votes(self.id)

    def vote_no(self, user_id):
        return CardStats.get_negative_votes(self.id)

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
                word, translated_word = word.split(':')[0], word.split(':')[1]
            else:
                translated_word = translate(word)
                sleep(0.5)
            card = db.session.query(Card).filter(Card.original_word==word).first()
            if card is None:
                try:
                    card = Card(original_word=word, translated_word=translated_word)
                    db.session.add(card)
                    db.session.commit()
                    category_and_card = CategoryCards(category_id=category.id, card_id=card.id)
                    db.session.add(category_and_card)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f'Not added, {card}, {e}')
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
            related_categories.append(category.name)
        related_categories = ', '.join(related_categories)
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


class CardStats(BaseModel):
    __tablename__ = 'card_stats'

    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    card = db.relationship('Card')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    vote = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now, index=True, nullable=False)

    @classmethod
    def add(cls, card, user, vote) -> bool:
        result = False
        try:
            card_stat = cls(card=card, user=user, vote=vote)
            db.session.add(card_stat)
            db.session.commit()
            return True 
        except:
            db.session.rollback()
            return False

    @classmethod
    def get_stats(cls, card_id, user_id=None):
        positive_votes = cls.get_positive_votes(card_id)
        negative_votes = cls.get_negative_votes(card_id)
        return positive_votes, negative_votes

    @classmethod
    def get_positive_votes(cls, card_id):
        return db.session.query(cls).filter(cls.card_id==card_id, cls.vote == 1).count()

    @classmethod
    def get_negative_votes(cls, card_id):
        return db.session.query(cls).filter(cls.card_id==card_id, cls.vote == -1).count()