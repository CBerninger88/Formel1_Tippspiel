from flask import Blueprint, render_template, request, jsonify
import requests

import utils
from city import City
from db import get_db

# Erstellen des Blueprints
wmStand_bp = Blueprint('wmStand', __name__)

# Registrieren von Routen bei dem Blueprint
@wmStand_bp.route('/wmStand')
def wmstand():
    return render_template('wmStand.html')

@wmStand_bp.route('/wmStand_get_cities', methods=['GET'])
def get_cities():
    return utils.get_cities()

@wmStand_bp.route('/wmStand_get_drivers', methods=['GET'])
def get_drivers():
    return jsonify(utils.get_drivers())


@wmStand_bp.route('/get_wm_stand_api', methods=['GET'])
def get_wm_stand_api():
    city = request.args.get('city').split(', ')[0].capitalize()

    if city == 'Melbourne':
        return jsonify({'success': False, 'message': 'Kein WM Stand bei erstem Rennen'}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT id FROM races WHERE city = %s', (city,))
    race_result = cursor.fetchone()
    if not race_result:
        return jsonify({'success': False, 'message': 'Race not found'}), 400
    race_id = race_result[0]

    season = 2024
    round_number = race_id-1

    url = f"https://ergast.com/api/f1/{season}/{round_number}/driverStandings.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        drivers = {}
        i = 0
        for driver_info in data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
            driver_name = f"{driver_info['Driver']['givenName'][0]}. {driver_info['Driver']['familyName']}"
            #points = driver_info['points']
            #team = driver_info['Constructors'][0]['name']
            drivers.update({f'wmdriver{i+1}': driver_name})
            i = i+1

        drivers.update({'success': True})
        return jsonify(drivers)
    else:
        return jsonify({'success': False, 'message': 'Keine Daten von API erhalten'}), 500



@wmStand_bp.route('/get_wm_stand')
def get_wm_stand():

    cityName = request.args.get('city').split(', ')[0].capitalize()

    city = City(cityName)
    ergebnis = {}
    wmdrivers, success = city.get_wm_stand()
    ergebnis.update(wmdrivers)
    ergebnis.update(success)

    return jsonify(ergebnis)



@wmStand_bp.route('/save_wm_stand', methods=['POST'])
def save_wm_stand():

    data = request.get_json()
    cityName = data['city'].split(', ')[0].capitalize()

    # WM Stand auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    wmStand = [data.get(f'wmdriver{i + 1}', '') for i in range(20)]

    city = City(cityName)

    city.set_wm_stand(wmStand)


    return jsonify({'success': True})