import psycopg2
from flask_login import current_user, login_required
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, jsonify, session, app


import utils
from db import get_db
from dummy import Dummytipps
from spieler import Spieler
from datetime import date
from datetime import datetime

# Erstellen des Blueprints
tippabgabe_bp = Blueprint('tippabgabe', __name__)

# Registrieren von Routen bei dem Blueprint
@tippabgabe_bp.route('/tippabgabe')
@tippabgabe_bp.route("/tippabgabe/tipprunde/<int:tipprunde_id>")
@login_required
def tippabgabe():
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
            "tippabgabe.html",
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

    return render_template("tippabgabe.html",
                           tipprunden=tipprunden,
                           users=users,
                           tipprunde_id=tipprunde_id
                           )


@tippabgabe_bp.route('/get_selection')
def get_selection():
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
    qdrivers, qstatus = spieler.get_quali_tipps(race_id, tipprunde_id)
    rdrivers, rstatus = spieler.get_race_tipps(race_id, tipprunde_id)
    fdriver, fstatus = spieler.get_fastestlab_tipp(race_id, tipprunde_id)
    drivers.update(qdrivers)
    drivers.update(rdrivers)
    drivers.update(fdriver)

    heute = date.today()
    renndatum = datetime.strptime(request.args.get('city').split(', ')[1], "%Y-%m-%d").date()
    if (renndatum - heute).days < 3:
        if not qstatus['success']:
            qdrivers = spieler.get_quali_tipps(race_id-1, tipprunde_id)[0]
            drivers.update(qdrivers)
            spieler.set_quali_tipps(race_id, [qdrivers.get(f'qdriver{i+1}', '') for i in range(4)], tipprunde_id)
        if not rstatus['success']:
            rdrivers = spieler.get_race_tipps(race_id-1, tipprunde_id)[0]
            drivers.update(rdrivers)
            spieler.set_race_tipps(race_id, [rdrivers.get(f'rdriver{i+1}', '') for i in range(10)], tipprunde_id)
        if not fstatus['success']:
            fdriver = spieler.get_fastestlab_tipp(race_id-1, tipprunde_id)[0]
            drivers.update(fdriver)
            spieler.set_fastestLab_tipps(race_id, fdriver['fdriver'], tipprunde_id)
        drivers.update({'zeitschranke': True})

    else:
        drivers.update({'zeitschranke': False})

    return jsonify(drivers)

@tippabgabe_bp.route('/get_dummy')
def get_dummy():
    name = request.args.get('name')
    city = request.args.get('city').split(', ')[0].capitalize()

    race_data = utils.get_raceID(city)
    if not race_data.get('success'):
        return jsonify({'drivers': {}, 'status': {'success': False, 'message': 'Race ID nicht gefunden'}})

    race_id = race_data['race_id']
    dummy = Dummytipps(name)

    # Fahrer-Tipps abrufen
    qualitipps, qstatus = dummy.get_quali_tipps(race_id)
    racetipps, rstatus = dummy.get_race_tipps(race_id)
    fastestlabtipps, fstatus = dummy.get_fastestlab_tipp(race_id)

    # Daten zusammenführen
    drivers = {**qualitipps, **racetipps, **fastestlabtipps}

    # Status berechnen
    success = all([qstatus.get('success'), rstatus.get('success'), fstatus.get('success')])
    message = f"Quali: {qstatus.get('message', 'Kein Status')}, Race: {rstatus.get('message', 'Kein Status')}, Fastest Lap: {fstatus.get('message', 'Kein Status')}"

    return jsonify({'drivers': drivers, 'status': {'success': success, 'message': message}})


@tippabgabe_bp.route('/save_selection', methods=['POST'])
def save_selection():
    data = request.get_json()
    name =current_user.username
    city = data['city'].split(', ')[0].capitalize()
    tipprunde_id = data['tipprunde_id']
    saison = app.current_app.config['SAISON']

    if tipprunde_id is None:
        tipprunde_id = 0

    # Quali-Fahrer (1-4), race fahrer (1-10), fastestLab Fahrer auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    qdrivers = [data.get(f'qdriver{i+1}', '') for i in range(4)]
    rdrivers = [data.get(f'driver{i + 1}', '') for i in range(10)]
    fdriver = data.get(f'fdriver', '')

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return race_id
    else:
        race_id = race_id['race_id']

    spieler = Spieler(name)
    spieler.set_quali_tipps(race_id, qdrivers, tipprunde_id)
    spieler.set_race_tipps(race_id, rdrivers, tipprunde_id)
    spieler.set_fastestLab_tipps(race_id, fdriver, tipprunde_id)

    return jsonify({'success': True})


@tippabgabe_bp.route('/races_get_cities', methods=['GET'])
def get_cities():
    saison = app.current_app.config['SAISON']
    cities = utils.get_cities(saison)
    rennliste = [f"{name.upper() if details['is_sprint'] else name}, {details['datum']}" for name, details in
                 cities.items()]
    return jsonify(rennliste)


@tippabgabe_bp.route('/get_drivers', methods=['GET'])
def get_drivers():
    return jsonify(utils.get_drivers())

@tippabgabe_bp.route('/get_users', methods=['GET'])
def get_users():
    return utils.get_users()
