from flask import Blueprint, render_template, request, jsonify

import utils
from spieler import Spieler

# Erstellen des Blueprints
sprinttipps_bp = Blueprint('sprinttipps', __name__)

# Registrieren von Routen bei dem Blueprint
@sprinttipps_bp.route('/sprinttipps')
def sprinttipps():
    return render_template('sprinttipps.html')

@sprinttipps_bp.route('/get_sprinttipps')
def get_sprinttipps():
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
    drivers.update(spieler.get_sprint_tipps(race_id))

    return jsonify(drivers)

@sprinttipps_bp.route('/save_sprinttipps', methods=['POST'])
def save_sprinttipps():
    data = request.get_json()
    name = data['name']
    city = data['city'].split(', ')[0].capitalize()

    # Race Fahrer 1-3 auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    sdrivers = [data.get(f'sdriver{i + 1}', '') for i in range(8)]

    race_id = utils.get_raceID(city)
    if not race_id['success']:
        return race_id
    else:
        race_id = race_id['race_id']

    spieler = Spieler(name)
    spieler.set_sprint_tipps(race_id, sdrivers)

    return jsonify({'success': True})


@sprinttipps_bp.route('/sprint_get_cities', methods=['GET'])
def get_cities():
    return utils.get_sprintCities()

@sprinttipps_bp.route('/get_drivers', methods=['GET'])
def get_drivers():
    return jsonify(utils.get_drivers())

@sprinttipps_bp.route('/get_users', methods=['GET'])
def get_users():
    return utils.get_users()
