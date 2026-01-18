import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, jsonify, session, app
from flask_login import current_user

import utils
from db import get_db
from spieler import Spieler
from datetime import date
from datetime import datetime

# Erstellen des Blueprints
zusatztipps_bp = Blueprint('zusatztipps', __name__)

# Registrieren von Routen bei dem Blueprint
@zusatztipps_bp.route('/zusatztipps')
def zusatztipps():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # 🔹 Tipprunden des aktuellen Users
    cursor.execute("""
                SELECT t.id, t.name
                FROM tipprunden t
                JOIN tipprunden_user tu ON tu.tipprunde_id = t.id
                WHERE tu.user_id = %s
                ORDER BY t.name
            """, (current_user.id,))
    tipprunden = cursor.fetchall()

    # 🔹 Fall: User ist in keiner Tipprunde
    if not tipprunden:
        return render_template(
            "zusatztipps.html",
            tipprunden=[],
            users=[current_user],
            tipprunde_id=None
        )

    # 🔹 Fallback: erste Tipprunde
    tipprunde_id = session.get('tipprunde_id') or tipprunden[0]['id']

    # 🔹 User der aktiven Tipprunde
    users = utils.get_users_in_tipprunde(tipprunde_id)

    return render_template("zusatztipps.html",
                           tipprunden=tipprunden,
                           users=users,
                           tipprunde_id=tipprunde_id
                           )


@zusatztipps_bp.route('/get_zusatztipps')
def get_zusatztipps():
    user_id = current_user.id
    tipprunde_id = request.args.get('tipprunde_id')
    saison = app.current_app.config['SAISON']

    if tipprunde_id is None:
        tipprunde_id = 0

    data = utils.get_zusatztipps(user_id, tipprunde_id, saison)

    heute = date.today()
    renndatum = date(2026,3,15)
    if (renndatum - heute).days < 3:
        data.update({'zeitschranke': True})

    return jsonify(data)

@zusatztipps_bp.route('/save_zusatztipps', methods=['POST'])
def save_zusatztipps():
    data = request.get_json()

    # user_id und saison hinzufügen
    data['user_id'] = current_user.id
    data['saison'] = app.current_app.config['SAISON']

    utils.set_zusatztipp(data)

    return jsonify({'success': True})


@zusatztipps_bp.route('/get_drivers', methods=['GET'])
def get_drivers():
    return jsonify(utils.get_drivers())


@zusatztipps_bp.route('/get_teams', methods=['GET'])
def get_teams():
    return jsonify(['Mercedes', 'Ferrari', 'Red Bull', 'Racing Bulls', 'McLaren', 'Cadillac', 'Haas', 'Williams', 'Alpine', 'Aston Martin', 'Audi' ])


