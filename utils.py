from db import get_db
from flask import jsonify

def get_cities():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT city, id, date, is_sprint FROM races ORDER BY date ASC;")
    result = cursor.fetchall()

    # Liste der Städte extrahieren
    cities = {
        name: {
            "race_id": race_id,
            "datum": datum,
            "is_sprint": is_sprint
        }
        for name, race_id, datum, is_sprint in result
    }
    return cities

def get_sprintCities():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT city, date, is_sprint FROM races WHERE is_sprint ORDER BY date ASC;")
    result = cursor.fetchall()

    # Liste der Städte extrahieren
    sprintcities = [f'{row[0].upper() if row[2] else row[0]}, {row[1]}' for row in result]

    return jsonify(sprintcities)


def get_drivers():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM drivers ORDER BY name ASC;")
    result = cursor.fetchall()

    # Liste der Fahrer extrahieren
    drivers = [row[0] for row in result]

    return drivers

def get_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM users ORDER BY id ASC;")
    result = cursor.fetchall()

    # Liste der Städte extrahieren
    users = [row[0] for row in result]

    return users

def get_raceID(city):
    db = get_db()
    cursor = db.cursor()
    # 2. race_id ermitteln
    cursor.execute('SELECT id FROM races WHERE city = %s', (city,))
    race_result = cursor.fetchone()
    if not race_result:
        return {'success': False, 'message': 'Race not found'}
    else:
        race_id = {'success': True, 'message': 'Race not found', 'race_id': race_result[0]}
        return race_id

def get_cityName(race_id):
    db = get_db()
    cursor = db.cursor()
    # 2. race_id ermitteln
    cursor.execute('SELECT city FROM races WHERE id = %s', (race_id,))
    race_result = cursor.fetchone()
    if not race_result:
        return {'success': False, 'message': 'Race not found'}
    else:
        race_id = {'success': True, 'message': 'Race not found', 'cityName': race_result[0]}
        return race_id

def is_sprint(city):
    db = get_db()
    cursor = db.cursor()
    # 2. race_id ermitteln
    cursor.execute('SELECT is_sprint FROM races WHERE city = %s', (city,))
    result = cursor.fetchone()
    if not result:
        return {'success': False, 'message': 'Race not found'}
    else:
        is_sprint = result[0]
        return is_sprint


def get_tipper(race_id, table_name):
    db = get_db()
    cursor = db.cursor()
    query = f"""
        SELECT DISTINCT u.name
        FROM {table_name} t
        JOIN users u ON t.user_id = u.id
        WHERE t.race_id = %s;
    """
    cursor.execute(query, (race_id,))
    result = cursor.fetchall()
    names = [row[0] for row in result]
    return names

