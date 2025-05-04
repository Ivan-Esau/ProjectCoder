import os
from flask import (
    Flask, render_template, request,
    jsonify, redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from models import db, User, APIKey
from storage.project_storage import create_project_structure
from storage.plan_storage    import save_plan
from storage.ticket_storage  import save_tickets
from storage.test_storage    import save_tests
from storage.code_storage    import save_code
from storage.saver           import save_response
from planner.planner         import generate_project_plan
from planner.ticket_generator import generate_tickets
from planner.test_generator   import generate_tests
from planner.code_generator   import generate_code_for_ticket

def create_app(config: dict = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Grund-Konfiguration
    app.config.update(
        SECRET_KEY="replace-with-your-secret",
        SQLALCHEMY_DATABASE_URI="sqlite:///users.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    if config:
        app.config.update(config)

    # Extensions
    db.init_app(app)
    login_mgr = LoginManager()
    login_mgr.login_view = "login"
    login_mgr.init_app(app)

    # Tabellen (bei Start)
    with app.app_context():
        db.create_all()

    @login_mgr.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username'].strip()
            password = request.form['password']
            if not username or not password:
                flash('Benutzername und Passwort erforderlich.')
                return redirect(url_for('register'))
            if User.query.filter_by(username=username).first():
                flash('Benutzername existiert bereits.')
                return redirect(url_for('register'))
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username'].strip()
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                flash('Ungültige Zugangsdaten.')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html', username=current_user.username)

    def _get_api_key(api_url, provided_key, model):
        if provided_key:
            rec = APIKey.query.filter_by(
                user_id=current_user.id,
                api_url=api_url
            ).first()
            if rec:
                rec.api_key_value = provided_key
                rec.model = model
            else:
                rec = APIKey(
                    api_url=api_url,
                    api_key_value=provided_key,
                    model=model,
                    user_id=current_user.id
                )
                db.session.add(rec)
            db.session.commit()
            return provided_key
        rec = APIKey.query.filter_by(
            user_id=current_user.id,
            api_url=api_url
        ).first()
        return rec.api_key_value if rec else ""

    @app.route('/plan', methods=['POST'])
    @login_required
    def plan():
        data = request.json or {}
        api_url      = data.get('api_url', '').strip()
        api_key      = data.get('api_key', '').strip()
        model        = data.get('model', '').strip()
        project_name = data.get('project_name', '').strip()
        project_desc = data.get('project_desc', '').strip()
        project_path = data.get('project_path', '').strip()

        # Validierung aller erforderlichen Felder
        if not api_url or not project_name or not project_desc or not project_path:
            return jsonify({
                "error": "API-URL, Projektname, Beschreibung & Pfad nötig"
            }), 400

        key = _get_api_key(api_url, api_key, model)
        try:
            # Basis-Pfad an create_project_structure übergeben
            project_folder = create_project_structure(
                project_name,
                base_path=project_path
            )
            plan_text = generate_project_plan(api_url, key, project_name, model)
            save_plan(project_folder, plan_text)
            # Logging: Eingabe ist jetzt die Projektbeschreibung
            save_response(project_folder, project_desc, plan_text)
            return jsonify({
                "plan": plan_text,
                "project_folder": project_folder
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Rest der Endpunkte bleibt unverändert…
    # /tickets, /generate_tests, /generate_code, /structure, /file_content

    @app.route('/tickets', methods=['POST'])
    @login_required
    def tickets():
        data           = request.json or {}
        api_url        = data.get('api_url', '').strip()
        api_key        = data.get('api_key', '').strip()
        model          = data.get('model', '').strip()
        project_folder = data.get('project_folder', '').strip()
        plan_text      = data.get('plan_text', '').strip()

        if not api_url or not project_folder or not plan_text:
            return jsonify(error="Fehlende Daten"), 400

        key = _get_api_key(api_url, api_key, model)
        try:
            tickets = generate_tickets(api_url, key, plan_text, model)
            save_tickets(project_folder, tickets)
            save_response(project_folder, plan_text, str(tickets))
            return jsonify(tickets=tickets)
        except ValueError as e:
            return jsonify(error=str(e)), 500
        except Exception:
            return jsonify(error="Unbekannter Fehler beim Ticket-Generieren."), 500

    @app.route('/generate_tests', methods=['POST'])
    @login_required
    def gen_tests():
        data           = request.json or {}
        api_url        = data.get('api_url', '').strip()
        api_key        = data.get('api_key', '').strip()
        model          = data.get('model', '').strip()
        project_folder = data.get('project_folder', '').strip()
        ticket_obj     = data.get('ticket')
        if not api_url or not project_folder or not ticket_obj:
            return jsonify(error="API-URL, Projektordner und Ticket erforderlich."), 400

        key = _get_api_key(api_url, api_key, model)
        try:
            tests_md   = generate_tests(api_url, key, ticket_obj, model)
            tests_file = save_tests(project_folder, ticket_obj["file_path"], tests_md)
            save_response(project_folder, ticket_obj["file_path"], tests_md)
            return jsonify(tests=tests_md, saved_test=tests_file)
        except Exception as e:
            return jsonify(error=str(e)), 500

    @app.route('/generate_code', methods=['POST'])
    @login_required
    def gen_code():
        data           = request.json or {}
        api_url        = data.get('api_url', '').strip()
        api_key        = data.get('api_key', '').strip()
        model          = data.get('model', '').strip()
        project_folder = data.get('project_folder', '').strip()
        ticket_obj     = data.get('ticket')
        if not api_url or not project_folder or not ticket_obj:
            return jsonify(error="API-URL, Projektordner und Ticket erforderlich."), 400

        key = _get_api_key(api_url, api_key, model)
        try:
            code_md   = generate_code_for_ticket(api_url, key, project_folder, ticket_obj, model)
            code_file = save_code(project_folder, ticket_obj["file_path"], code_md)
            save_response(project_folder, ticket_obj["file_path"], code_md)
            return jsonify(code=code_md, saved_to=code_file)
        except Exception as e:
            return jsonify(error=str(e)), 500

    @app.route('/structure', methods=['POST'])
    @login_required
    def structure():
        data           = request.json or {}
        project_folder = data.get('project_folder', '').strip()
        if not project_folder:
            return jsonify(error="Projektordner erforderlich."), 400

        tree = {}
        for root, dirs, files in os.walk(project_folder):
            rel = os.path.relpath(root, project_folder)
            node = tree
            if rel != '.':
                for part in rel.split(os.sep):
                    node = node.setdefault(part, {})
            for d in dirs:
                node.setdefault(d, {})
            for f in files:
                node[f] = None
        return jsonify(structure=tree)

    @app.route('/file_content', methods=['POST'])
    @login_required
    def file_content():
        data           = request.json or {}
        project_folder = data.get('project_folder', '').strip()
        file_path      = data.get('file_path', '').strip()
        if not project_folder or not file_path:
            return jsonify(error="Projektordner und file_path erforderlich."), 400

        abs_path = os.path.join(project_folder, file_path)
        try:
            with open(abs_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return jsonify(error=str(e)), 500
        return jsonify(content=content)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
