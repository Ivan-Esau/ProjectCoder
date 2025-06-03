import pytest
import json
from pathlib import Path
from web_app import create_app
from models import db, User, APIKey

@pytest.fixture
def app(tmp_path):
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path/'test.db'}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret",
    }
    app = create_app(config)
    with app.app_context():
        db.create_all()
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def register_and_login(client):
    rv = client.post("/register", data={"username": "alice", "password": "secret"}, follow_redirects=True)
    assert rv.status_code == 200
    rv = client.post("/login", data={"username": "alice", "password": "secret"}, follow_redirects=True)
    assert rv.status_code == 200
    return client

def test_register_login_logout(client):
    rv = client.post("/register", data={"username":"bob","password":"pw"}, follow_redirects=True)
    assert "Login" not in rv.get_data(as_text=True)
    rv = client.get("/logout", follow_redirects=True)
    assert "Login" in rv.get_data(as_text=True)

def test_plan_endpoint_requires_auth(client):
    rv = client.post("/plan", json={})
    assert rv.status_code == 302
    assert "/login" in rv.headers["Location"]

def test_plan_endpoint_bad_request(client):
    client = register_and_login(client)
    rv = client.post("/plan", json={
        "api_url": "",
        "project_name": "",
        "project_desc": ""
    })
    assert rv.status_code == 400
    # Now returns JSON error
    assert rv.get_json() == {"error": "API-URL, Projektname & Beschreibung nötig"}

def test_plan_success(monkeypatch, client):
    client = register_and_login(client)
    monkeypatch.setattr("web_app.generate_project_plan", lambda u,k,p,m: "MEIN_PLAN")
    monkeypatch.setattr("web_app.create_project_structure", lambda name, base_path=None: "/tmp/proj1")
    rv = client.post("/plan", json={
        "api_url": "u",
        "project_name": "Mein_Testprojekt",
        "project_desc": "Beschreibung",
        "model": "gpt-test"
    })
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["plan"] == "MEIN_PLAN"
    assert data["project_folder"] == "/tmp/proj1"

def test_tickets_endpoint_requires_auth(client):
    rv = client.post("/tickets", json={})
    assert rv.status_code == 302
    assert "/login" in rv.headers["Location"]

def test_tickets_bad_request(client):
    client = register_and_login(client)
    rv = client.post("/tickets", json={"api_url": "", "project_folder": "", "plan_text": ""})
    assert rv.status_code == 400
    assert rv.get_json() == {"error": "Fehlende Daten"}

def test_tickets_parse_error(monkeypatch, client):
    client = register_and_login(client)
    monkeypatch.setattr("web_app.generate_tickets",
        lambda u,k,p,m: (_ for _ in ()).throw(ValueError("Parsing-Fehler")))
    rv = client.post("/tickets", json={"api_url":"u","project_folder":"/tmp","plan_text":"p"})
    assert rv.status_code == 500
    assert "Parsing-Fehler" in rv.get_json()["error"]

def test_tickets_success(monkeypatch, client):
    client = register_and_login(client)
    monkeypatch.setattr("web_app.generate_tickets", lambda u,k,p,m: [{"title":"T1"}])
    monkeypatch.setattr("web_app.save_tickets", lambda f,t: None)
    rv = client.post("/tickets", json={"api_url":"u","project_folder":"/tmp","plan_text":"p"})
    assert rv.status_code == 200
    assert rv.get_json()["tickets"][0]["title"] == "T1"

def test_structure_and_file_content(client, tmp_path):
    client = register_and_login(client)
    proj = tmp_path/"projectA"
    (proj/"src").mkdir(parents=True)
    (proj/"src"/"mod.py").write_text("print('hello')", encoding="utf-8")

    rv = client.post("/structure", json={"project_folder": str(proj)})
    assert rv.status_code == 200
    struct = rv.get_json()["structure"]
    assert "src" in struct and "mod.py" in struct["src"]

    rv = client.post("/file_content", json={
        "project_folder": str(proj),
        "file_path": "src/mod.py"
    })
    assert rv.status_code == 200
    assert "print('hello')" in rv.get_json()["content"]
