"""
models.py

Dieses Modul definiert die ORM-Modelle für die Anwendung:

- User: Repräsentiert einen Benutzerdatensatz mit Authentifizierung und zugehörigen API-Schlüsseln.
- APIKey: Speichert die API-Zugangsdaten eines Users für verschiedene AI-Services.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    ORM-Modell für einen registrierten Benutzer.

    Attributes:
        id (int): Primärschlüssel des Benutzers.
        username (str): Eindeutiger Benutzername (max. 150 Zeichen).
        password_hash (str): Gehashtes Passwort (max. 256 Zeichen).
        api_keys (List[APIKey]): Beziehung zu den APIKey-Einträgen dieses Benutzers.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    api_keys = db.relationship('APIKey', backref='user', lazy=True)

    def set_password(self, pw: str) -> None:
        """
        Erzeugt aus einem Klartext-Passwort einen sicheren Hash
        und speichert ihn in `self.password_hash`.

        Args:
            pw (str): Das Klartext-Passwort des Benutzers.
        """
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        """
        Überprüft, ob ein Klartext-Passwort zum gespeicherten Hash passt.

        Args:
            pw (str): Das Klartext-Passwort zur Überprüfung.

        Returns:
            bool: True, wenn das Passwort korrekt ist, ansonsten False.
        """
        return check_password_hash(self.password_hash, pw)


class APIKey(db.Model):
    """
    ORM-Modell für API-Schlüssel, die einem Benutzer zugeordnet sind.

    Attributes:
        id (int): Primärschlüssel des APIKey-Eintrags.
        api_url (str): Basis-URL des AI-Service-Endpunkts.
        api_key_value (str): Der API-Schlüssel oder Token.
        model (str): Optionaler Modellname zur Verwendung (z. B. "gpt-4").
        user_id (int): Fremdschlüssel zu dem zugehörigen User.
        user (User): Backreference zum entsprechenden User-Objekt.
    """
    id = db.Column(db.Integer, primary_key=True)
    api_url = db.Column(db.String(300), nullable=False)
    api_key_value = db.Column(db.String(500), nullable=False)
    model = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
