from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(250))
    joined_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'{self.username.capitalize()}'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('blogs', lazy=True,
                                                      cascade='save-update, merge, delete, delete-orphan'))

    def __init__(self, title, intro, text, user_id):
        self.title = title
        self.intro = intro
        self.text = text
        self.user_id = user_id

    def __repr__(self):
        return f'{self.title}, {self.intro}, {self.date}'


@manager.user_loader
def load_user(id):
    return db.session.query(User).get(id)
