from flask import Blueprint, render_template

regeln_bp = Blueprint('regeln', __name__)

@regeln_bp.route('/regeln')
def regeln():
    return render_template('regeln.html')