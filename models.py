from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    api_keys      = db.relationship('APIKey', backref='user', lazy=True)

    def set_password(self, pw):  self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

class APIKey(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    api_url       = db.Column(db.String(300), nullable=False)
    api_key_value = db.Column(db.String(500), nullable=False)
    model         = db.Column(db.String(100), nullable=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
