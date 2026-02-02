import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, jsonify, session, app
from flask_login import current_user

from models import utils
from models.db import get_db
from models.spieler import Spieler
from datetime import date
from datetime import datetime

# Erstellen des Blueprints
sprinttipps_bp = Blueprint('sprinttipps', __name__)

# Registrieren von Routen bei dem Blueprint
@sprinttipps_bp.route('/sprinttipps')
def sprinttipps():
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
            "sprinttipps.html",
            tipprunden=[],
            users=[current_user],
            tipprunde_id=None
        )

    # 🔹 Fallback: erste Tipprunde
    tipprunde_id = session.get('tipprunde_id') or tipprunden[0]['id']

    # 🔹 User der aktiven Tipprunde
    users = utils.get_users_in_tipprunde(tipprunde_id)

    return render_template("sprinttipps.html",
                           tipprunden=tipprunden,
                           users=users,
                           tipprunde_id=tipprunde_id
                           )


@sprinttipps_bp.route('/get_sprinttipps')
def get_sprinttipps():
    name = current_user.username
    city = request.args.get('city').split(', ')[0].capitalize()
    tipprunde_id = request.args.get('tipprunde_id')
    saison = app.current_app.config['SAISON']

    if tipprunde_id is None:
        tipprunde_id = 0

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return {}
    else:
        race_id = race_id['race_id']

    spieler = Spieler(name)
    drivers = {}
    drivers.update(spieler.get_sprint_tipps(race_id, tipprunde_id)[0])

    heute = date.today()
    renndatum = datetime.strptime(request.args.get('city').split(', ')[1], "%Y-%m-%d").date()
    if (renndatum - heute).days < 3:
        drivers.update({'zeitschranke': True})

    return jsonify(drivers)

@sprinttipps_bp.route('/save_sprinttipps', methods=['POST'])
def save_sprinttipps():
    data = request.get_json()
    name = current_user.username
    city = data['city'].split(', ')[0].capitalize()
    tipprunde_id = data['tipprunde_id']
    saison = app.current_app.config['SAISON']

    # Race Fahrer 1-3 auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    sdrivers = [data.get(f'sdriver{i + 1}', '') for i in range(8)]

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return race_id
    else:
        race_id = race_id['race_id']

    spieler = Spieler(name)
    spieler.set_sprint_tipps(race_id, sdrivers, tipprunde_id)

    return jsonify({'success': True})


@sprinttipps_bp.route('/sprint_get_cities', methods=['GET'])
def get_cities():
    saison = app.current_app.config['SAISON']
    cities = utils.get_sprintCities(saison)
    rennliste = [f"{name.upper() if details['is_sprint'] else next}, {details['datum']}" for name, details in
                 cities.items()]
    return jsonify(rennliste)

@sprinttipps_bp.route('/get_drivers', methods=['GET'])
def get_drivers():
    return jsonify(utils.get_drivers())


