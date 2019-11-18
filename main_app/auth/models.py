from datetime import datetime
from main_app.database import db
from flask_login import UserMixin


class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {'sqlite_autoincrement': True}     # remove if postgres
    id = db.Column(db.Integer(), primary_key=True)


class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    
    name = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_logged_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @classmethod
    def get(cls, user_id):
        try:
            return db.session.query(User).get(user_id)
        except NoResultFound:
            return None
    
    @classmethod
    def get_by_email(cls, email: str):
        return db.session.query(User).filter(User.email == email).first()

    @classmethod
    def check_exists(cls, email: str) -> bool:
        return bool(db.session.query(User).filter(User.email == email).first())

    @classmethod
    def get_or_none(cls, email: str, password_hash: str):
        user = db.session.query(User).filter(User.email == email, User.password == password_hash).first()
        return user
