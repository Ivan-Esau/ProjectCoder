import pytest
from models import User, APIKey, db
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update({"SQLALCHEMY_DATABASE_URI":"sqlite:///:memory:", "SQLALCHEMY_TRACK_MODIFICATIONS":False})
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_password_hashing(app):
    u = User(username="alice")
    u.set_password("secret")
    assert u.password_hash != "secret"              # wirklich gehasht
    assert u.check_password("secret") is True       # richtiges PW
    assert u.check_password("wrong")  is False      # falsches PW

def test_api_key_relationship(app):
    u = User(username="bob")
    u.set_password("pw")
    db.session.add(u)
    db.session.commit()

    key = APIKey(api_url="url", api_key_value="KEY", model="m", user_id=u.id)
    db.session.add(key)
    db.session.commit()

    assert len(u.api_keys) == 1
    assert u.api_keys[0].api_key_value == "KEY"
