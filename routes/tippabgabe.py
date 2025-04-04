from flask import Blueprint, render_template, request, jsonify


import utils
from dummy import Dummy
from spieler import Spieler
from datetime import date
from datetime import datetime

# Erstellen des Blueprints
tippabgabe_bp = Blueprint('tippabgabe', __name__)

# Registrieren von Routen bei dem Blueprint
@tippabgabe_bp.route('/tippabgabe')
def tippabgabe():
    return render_template('tippabgabe.html')

@tippabgabe_bp.route('/get_selection')
def get_selection():
    name = request.args.get('name')
    city = request.args.get('city').split(', ')[0].capitalize()

    if name not in utils.get_users():
       return {}

    race_id = utils.get_raceID(city)
    if not race_id['success']:
        return {}
    else:
        race_id = race_id['race_id']

    spieler = Spieler(name)
    drivers = {}
    drivers.update(spieler.get_quali_tipps(race_id)[0])
    drivers.update(spieler.get_race_tipps(race_id)[0])
    drivers.update(spieler.get_fastestlab_tipp(race_id)[0])

    heute = date.today()
    renndatum = datetime.strptime(request.args.get('city').split(', ')[1], "%Y-%m-%d").date()
    if (renndatum - heute).days < 3 and name not in ['Ergebnis', 'Dummy_LY', 'Dummy_WM', 'Dummy_LR']:
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
    dummy = Dummy(name)

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
    name = data['name']
    city = data['city'].split(', ')[0].capitalize()

    # Quali-Fahrer (1-4), race fahrer (1-10), fastestLab Fahrer auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    qdrivers = [data.get(f'qdriver{i+1}', '') for i in range(4)]
    rdrivers = [data.get(f'driver{i + 1}', '') for i in range(10)]
    fdriver = data.get(f'fdriver', '')

    race_id = utils.get_raceID(city)
    if not race_id['success']:
        return race_id
    else:
        race_id = race_id['race_id']

    spieler = Spieler(name)
    spieler.set_quali_tipps(race_id, qdrivers)
    spieler.set_race_tipps(race_id, rdrivers)
    spieler.set_fastestLab_tipps(race_id, fdriver)

    return jsonify({'success': True})


@tippabgabe_bp.route('/races_get_cities', methods=['GET'])
def get_cities():
    return utils.get_cities()


@tippabgabe_bp.route('/get_drivers', methods=['GET'])
def get_drivers():
    return jsonify(utils.get_drivers())

@tippabgabe_bp.route('/get_users', methods=['GET'])
def get_users():
    return utils.get_users()
