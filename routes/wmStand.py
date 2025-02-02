from flask import Blueprint, render_template, request, jsonify
import requests
from db import get_db

# Erstellen des Blueprints
wmStand_bp = Blueprint('wmStand', __name__)

# Registrieren von Routen bei dem Blueprint
@wmStand_bp.route('/wmStand')
def wmstand():
    return render_template('wmStand.html')

@wmStand_bp.route('/wmStand_get_cities', methods=['GET'])
def get_cities():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT city, date FROM races ORDER BY date ASC;")
    result = cursor.fetchall()

    # Liste der Städte extrahieren
    cities = [f'{row[0]}, {row[1]}' for row in result]

    return jsonify(cities)

@wmStand_bp.route('/wmStand_get_drivers', methods=['GET'])
def get_drivers():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM drivers ORDER BY name ASC;")
    result = cursor.fetchall()

    # Liste der Städte extrahieren
    drivers = [row[0] for row in result]

    return jsonify(drivers)


@wmStand_bp.route('/get_wm_stand', methods=['GET'])
def get_wm_stand():
    city = request.args.get('city').split(', ')[0]

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

        return jsonify(drivers)
    else:
        return jsonify({"error": "Fehler beim Abrufen der WM-Stände"}), 500
