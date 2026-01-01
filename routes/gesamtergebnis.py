import psycopg2
from flask_login import current_user
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, jsonify, session, app

import utils
from datetime import date
from datetime import datetime

from db import get_db
from spieler import Spieler

# Erstellen des Blueprints
gesamtergebnis_bp = Blueprint('gesamtergebnis', __name__)

# Registrieren von Routen bei dem Blueprint
@gesamtergebnis_bp.route('/gesamtergebnis')
def gesamtnergebnis():
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
            "gesamtergebnis.html",
            tipprunden=[],
            users=[current_user],
            tipprunde_id=None
        )

    # 🔹 Fallback: erste Tipprunde
    tipprunde_id = session.get('tipprunde_id') or tipprunden[0]['id']

    # 🔹 User der aktiven Tipprunde
    cursor.execute("""
                SELECT u.id, u.username
                FROM users u
                JOIN tipprunden_user tu ON tu.user_id = u.id
                WHERE tu.tipprunde_id = %s
                ORDER BY u.username
            """, (tipprunde_id,))
    users = cursor.fetchall()

    return render_template("gesamtergebnis.html",
                           tipprunden=tipprunden,
                           users=users,
                           tipprunde_id=tipprunde_id
                           )

@gesamtergebnis_bp.route('/get_gesamtpunkte',  methods=['POST'])
def get_gesamtpunkte():

    spieler = utils.get_users()
    heute = date.today()
    stichtag = datetime(2025, 3, 20)
    saison = app.current_app.config['SAISON']
    cities = utils.get_cities(saison)

    gefilterte_rennen = {
        name: details
        for name, details in cities.items()
        if details["datum"] <= heute
    }

    ergebnis = {}
    for name in spieler:
        if name == "Ergebnis":
            continue
        gesamtpunkte = 0
        for rennen in gefilterte_rennen:
            tippunkte = Spieler(name).get_tipppunkte(gefilterte_rennen[rennen]['race_id'])
            gesamtpunkte += sum(tippunkte.values())
        ergebnis[name] = gesamtpunkte

    ergebnis_sorted = sorted(ergebnis.items(), key=lambda item: item[1], reverse=True)


    status = {'success': True, 'message': 'Alles ok'}

    return jsonify({'spieler': ergebnis_sorted, 'status': status})