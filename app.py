from flask import Flask
from routes.home import home_bp
from routes.tabelle import tabelle_bp
from routes.tippabgabe import tippabgabe_bp
from routes.rennergebnis import rennergebnis_bp
from routes.gesamtergebnis import gesamtergebnis_bp
from routes.wmStand import wmStand_bp
from db import init_db, close_connection
import os

app = Flask(__name__)

# Registriere die Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(tabelle_bp)
app.register_blueprint(tippabgabe_bp)
app.register_blueprint(rennergebnis_bp)
app.register_blueprint(gesamtergebnis_bp)
app.register_blueprint(wmStand_bp)

# Schließe die Datenbankverbindung nach jeder Anfrage
app.teardown_appcontext(close_connection)

# Initialisiere die Datenbank

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    init_db(app)

    app.run(host='0.0.0.0', debug=False, port=port)

