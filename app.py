import psycopg2
from flask_mail import Mail
from psycopg2.extras import RealDictCursor
from flask import Flask
from flask_login import LoginManager
from flask_login import current_user

from routes.home import home_bp
from routes.sprinttipps import sprinttipps_bp
from routes.tabelle import tabelle_bp
from routes.tippabgabe import tippabgabe_bp
from routes.sprinttipps import sprinttipps_bp
from routes.rennergebnis import rennergebnis_bp
from routes.gesamtergebnis import gesamtergebnis_bp
from routes.wmStand import wmStand_bp
from routes.regeln import regeln_bp
from routes.auth import auth_bp
from routes.tipprunden import tipprunden_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from routes.zusatztipps import zusatztipps_bp
from routes.auth import mail
from db import get_db, init_db, close_connection
from models.user import User
import os
from dotenv import load_dotenv
load_dotenv()
from models.config import Config

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config.from_object(Config)

mail.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"  # wohin bei @login_required
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        return User(user["id"], user["username"], user["password_hash"], user["is_admin"])
    return None

# Registriere die Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(tabelle_bp)
app.register_blueprint(tippabgabe_bp)
app.register_blueprint(sprinttipps_bp)
app.register_blueprint(rennergebnis_bp)
app.register_blueprint(gesamtergebnis_bp)
app.register_blueprint(wmStand_bp)
app.register_blueprint(regeln_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(tipprunden_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(zusatztipps_bp)

# Schließe die Datenbankverbindung nach jeder Anfrage
app.teardown_appcontext(close_connection)

# Initialisiere die Datenbank

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    init_db(app)

    app.run(host='0.0.0.0', debug=False, port=port)

