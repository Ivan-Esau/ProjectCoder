"""
Dieses Modul definiert und konfiguriert die Flask-Anwendung für das Projekt-Management-Tool.
Es beinhaltet:
- Benutzer-Authentifizierung (Registrierung, Login, Logout)
- Endpunkte zur Projektplanung, Ticket-Generierung, Test- und Code-Erstellung
- Speicherung und Abruf von Logs, Projektstruktur und Dateiinhalten
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from models import db, User, APIKey
from storage.project_storage import create_project_structure
from storage.plan_storage import save_plan
from storage.ticket_storage import save_tickets
from storage.test_storage import save_tests
from storage.code_storage import save_code
from storage.saver import save_response
from planner.planner import generate_project_plan
from planner.ticket_generator import generate_tickets
from planner.test_generator import generate_tests
from planner.code_generator import generate_code_for_ticket
from scripts.gitlab_issues import create_issues_from_tickets


def create_app(config: dict = None) -> Flask:
    """
    Erzeugt und konfiguriert eine Flask-Anwendung mit allen benötigten Routen und Extensions.

    Args:
        config (dict, optional): Zusätzliche Konfiguration für Flask (überschreibt Defaults).

    Returns:
        Flask: Die initialisierte Flask-Applikation.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config.update(
        SECRET_KEY="replace-with-your-secret",
        SQLALCHEMY_DATABASE_URI="sqlite:///users.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    login_mgr = LoginManager()
    login_mgr.login_view = "login"
    login_mgr.init_app(app)

    with app.app_context():
        db.create_all()

    @login_mgr.user_loader
    def load_user(user_id: str) -> User:
        """Callback für flask-login, um den aktuellen Benutzer anhand seiner ID zu laden."""
        return User.query.get(int(user_id))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """
        GET:  Liefert die Registrierungsseite.
        POST: Legt bei gültigen Eingaben einen neuen User an und loggt ihn ein.
        """
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]
            if not username or not password:
                flash("Benutzername und Passwort erforderlich.")
                return redirect(url_for("register"))
            if User.query.filter_by(username=username).first():
                flash("Benutzername existiert bereits.")
                return redirect(url_for("register"))
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("index"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """
        GET:  Liefert die Login-Seite.
        POST: Prüft Zugangsdaten und loggt den User ein.
        """
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                flash("Ungültige Zugangsdaten.")
                return redirect(url_for("login"))
            login_user(user)
            return redirect(url_for("index"))
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        """Loggt den aktuellen Benutzer aus und leitet zur Login-Seite weiter."""
        logout_user()
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def index():
        """Startseite der Anwendung; zeigt das Dashboard mit Benutzernamen."""
        return render_template("index.html", username=current_user.username)

    def _get_api_key(api_url: str, provided_key: str, model: str) -> str:
        """
        Liest bestehenden APIKey aus der DB oder speichert einen neuen, wenn provided_key gesetzt ist.

        Args:
            api_url (str): Basis-URL des AI-Service.
            provided_key (str): Neuer API-Schlüssel vom Frontend (oder leer).
            model (str): Optionaler Modellname.

        Returns:
            str: Der final zu nutzende API-Key.
        """
        if provided_key:
            rec = APIKey.query.filter_by(
                user_id=current_user.id, api_url=api_url
            ).first()
            if rec:
                rec.api_key_value = provided_key
                rec.model = model
            else:
                rec = APIKey(
                    api_url=api_url,
                    api_key_value=provided_key,
                    model=model,
                    user_id=current_user.id,
                )
                db.session.add(rec)
            db.session.commit()
            return provided_key

        rec = APIKey.query.filter_by(user_id=current_user.id, api_url=api_url).first()
        return rec.api_key_value if rec else ""

    @app.route("/plan", methods=["POST"])
    @login_required
    def plan():
        data = request.json or {}
        api_url = data.get("api_url", "").strip()
        api_key = data.get("api_key", "").strip()
        model = data.get("model", "").strip()
        name = data.get("project_name", "").strip()
        desc = data.get("project_desc", "").strip()
        project = data.get("project", "").strip()
        base_path = data.get("project_path", "").strip()

        # Fallback: unterstützt alte API mit einfachem "project"-Feld
        if project:
            if not name:
                name = project
            if not desc:
                desc = project

        # Validierung: API-URL, Name und Beschreibung erforderlich
        if not api_url or not name or not desc:
            return jsonify({"error": "API-URL, Projektname & Beschreibung nötig"}), 400

        key = _get_api_key(api_url, api_key, model)
        try:
            # create_project_structure nimmt optional einen Basis-Pfad entgegen
            if base_path:
                project_folder = create_project_structure(name, base_path)
            else:
                project_folder = create_project_structure(name)
            project_text = f"{name}\n{desc}"
            plan_text = generate_project_plan(api_url, key, project_text, model)

            save_plan(project_folder, plan_text)
            save_response(project_folder, project_text, plan_text)
            return jsonify({"plan": plan_text, "project_folder": project_folder}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/tickets", methods=["POST"])
    @login_required
    def tickets():
        """
        Generiert Tickets aus einem vorhandenen Projektplan-Text,
        speichert sie und liefert die Liste zurück.
        """
        data = request.json or {}
        api_url = data.get("api_url", "").strip()
        api_key = data.get("api_key", "").strip()
        model = data.get("model", "").strip()
        project_folder = data.get("project_folder", "").strip()
        plan_text = data.get("plan_text", "").strip()

        if not api_url or not project_folder or not plan_text:
            return jsonify(error="Fehlende Daten"), 400

        key = _get_api_key(api_url, api_key, model)
        try:
            tickets = generate_tickets(api_url, key, plan_text, model)
            save_tickets(project_folder, tickets)
            save_response(project_folder, plan_text, str(tickets))
            return jsonify(tickets=tickets), 200
        except ValueError as e:
            return jsonify(error=str(e)), 500
        except Exception:
            return jsonify(error="Unbekannter Fehler beim Ticket-Generieren."), 500

    @app.route("/generate_tests", methods=["POST"])
    @login_required
    def gen_tests():
        """
        Generiert pytest-Tests für ein einzelnes Ticket,
        speichert die Tests und gibt Pfad & Inhalt zurück.
        """
        data = request.json or {}
        api_url = data.get("api_url", "").strip()
        api_key = data.get("api_key", "").strip()
        model = data.get("model", "").strip()
        project_folder = data.get("project_folder", "").strip()
        ticket_obj = data.get("ticket")

        if not api_url or not project_folder or not ticket_obj:
            return jsonify(error="API-URL, Projektordner und Ticket erforderlich."), 400

        key = _get_api_key(api_url, api_key, model)
        try:
            tests_md = generate_tests(api_url, key, ticket_obj, model)
            tests_file = save_tests(project_folder, ticket_obj["file_path"], tests_md)
            save_response(project_folder, ticket_obj["file_path"], tests_md)
            return jsonify(tests=tests_md, saved_test=tests_file), 200
        except Exception as e:
            return jsonify(error=str(e)), 500

    @app.route("/generate_code", methods=["POST"])
    @login_required
    def gen_code():
        """
        Generiert Code für ein einzelnes Ticket,
        speichert die Datei und gibt Pfad & Inhalt zurück.
        """
        data = request.json or {}
        api_url = data.get("api_url", "").strip()
        api_key = data.get("api_key", "").strip()
        model = data.get("model", "").strip()
        project_folder = data.get("project_folder", "").strip()
        ticket_obj = data.get("ticket")

        if not api_url or not project_folder or not ticket_obj:
            return jsonify(error="API-URL, Projektordner und Ticket erforderlich."), 400

        key = _get_api_key(api_url, api_key, model)
        try:
            code_md = generate_code_for_ticket(
                api_url, key, project_folder, ticket_obj, model
            )
            code_file = save_code(project_folder, ticket_obj["file_path"], code_md)
            save_response(project_folder, ticket_obj["file_path"], code_md)
            return jsonify(code=code_md, saved_to=code_file), 200
        except Exception as e:
            return jsonify(error=str(e)), 500

    @app.route("/gitlab_issues", methods=["POST"])
    @login_required
    def gitlab_issues():
        """Create GitLab issues from saved tickets."""
        data = request.json or {}
        project_folder = data.get("project_folder", "").strip()
        gitlab_url = data.get("gitlab_url", "").strip() or "https://gitlab.com"
        project_id = data.get("gitlab_project_id", "").strip()
        token = data.get("gitlab_token", "").strip()

        if not project_folder or not project_id or not token:
            return (
                jsonify(error="Projektordner, Projekt-ID und Token erforderlich."),
                400,
            )

        tickets_file = os.path.join(project_folder, "tickets", "tickets.json")
        if not os.path.exists(tickets_file):
            return jsonify(error="tickets.json nicht gefunden."), 400

        try:
            issues = create_issues_from_tickets(
                tickets_file, gitlab_url, project_id, token
            )
            return jsonify(issues=issues), 200
        except Exception as e:
            return jsonify(error=str(e)), 500

    @app.route("/structure", methods=["POST"])
    @login_required
    def structure():
        """
        Gibt die Ordner- und Dateistruktur des Projekts als JSON-Tree zurück.
        """
        data = request.json or {}
        project_folder = data.get("project_folder", "").strip()

        if not project_folder:
            return jsonify(error="Projektordner erforderlich."), 400

        tree = {}
        for root, dirs, files in os.walk(project_folder):
            rel = os.path.relpath(root, project_folder)
            node = tree
            if rel != ".":
                for part in rel.split(os.sep):
                    node = node.setdefault(part, {})
            for d in dirs:
                node.setdefault(d, {})
            for f in files:
                node[f] = None
        return jsonify(structure=tree), 200

    @app.route("/file_content", methods=["POST"])
    @login_required
    def file_content():
        """
        Liest den Inhalt einer Datei im Projektverzeichnis und liefert ihn als Text zurück.
        """
        data = request.json or {}
        project_folder = data.get("project_folder", "").strip()
        file_path = data.get("file_path", "").strip()

        if not project_folder or not file_path:
            return jsonify(error="Projektordner und file_path erforderlich."), 400

        abs_path = os.path.join(project_folder, file_path)
        try:
            with open(abs_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return jsonify(error=str(e)), 500
        return jsonify(content=content), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
