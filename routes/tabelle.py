from flask import Blueprint, render_template

# Erstellen des Blueprints
tabelle_bp = Blueprint('tabelle', __name__)

# Registrieren von Routen bei dem Blueprint
@tabelle_bp.route('/tabelle')
def tabelle():
    return render_template('tabelle.html')
