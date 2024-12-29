from flask import Blueprint, render_template

# Erstellen des Blueprints
rennergebnis_bp = Blueprint('rennergebnis', __name__)

# Registrieren von Routen bei dem Blueprint
@rennergebnis_bp.route('/rennergebnis')
def rennergebnis():
    return render_template('rennergebnis.html')
