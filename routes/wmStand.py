from flask import Blueprint, render_template

# Erstellen des Blueprints
wmStand_bp = Blueprint('wmStand', __name__)

# Registrieren von Routen bei dem Blueprint
@wmStand_bp.route('/wmStand')
def wmStand():
    return render_template('wmStand.html')
