from datetime import datetime
from random import randint
from sqlalchemy.orm.exc import NoResultFound
from flask_login import UserMixin
from main_app.database import db


class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {'sqlite_autoincrement': True}     # remove if postgres
    id = db.Column(db.Integer(), primary_key=True)


class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    
    name = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @classmethod
    def get(cls, user_id: int) -> User or None:
        try:
            return db.session.query(User).get(user_id)
        except NoResultFound:
            return None
    
    @classmethod
    def get_by_email(cls, email: str) -> User or None:
        return db.session.query(User).filter(User.email == email).first()

    @classmethod
    def check_exists(cls, email: str) -> bool:
        return bool(db.session.query(User).filter(User.email == email).first())

    @classmethod
    def get_or_none(cls, email: str, password_hash: str) -> User or None:
        user = db.session.query(User).filter(User.email == email, User.password == password_hash).first()
        return user


class UserSeed(BaseModel):
    __tablename__ = 'user_seeds'

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User')
    seed = db.Column(db.Integer())

    @classmethod
    def get_or_create(cls, user) -> int:
        if user.is_authenticated:
            try:
                user_seed = db.session.query(UserSeed).filter(UserSeed.user == user).one()
            except NoResultFound:
                user_seed = cls(user=user, seed=rand())
                db.session.add(user_seed)
                db.session.commit()
            return user_seed.seed
        else:
            try:
                default_seed = db.session.query(UserSeed).filter(UserSeed.user == None).one()
            except NoResultFound:
                default_seed = cls(seed=rand())
                db.session.add(default_seed)
                db.session.commit()
            return default_seed.seed

    @classmethod
    def get_by_user(cls, user) -> int:
        return cls.get_or_create(user)


    @classmethod
    def create_new_seed(cls, user) -> bool:
        if user.is_authenticated:
            user_seed = db.session.query(UserSeed).filter(UserSeed.user == user).one()
            user_seed.seed = rand()
            db.session.commit()
            return True
        else:
            default_seed = db.session.query(UserSeed).filter(UserSeed.user == None).one()
            default_seed.seed = rand()
            db.session.commit()
            return True
        return False


def rand() -> int:
    return randint(-100000, 100000)