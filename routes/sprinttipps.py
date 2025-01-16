from flask import Blueprint, render_template, request, jsonify
from db import get_db

# Erstellen des Blueprints
sprinttipps_bp = Blueprint('sprinttipps', __name__)

# Registrieren von Routen bei dem Blueprint
@sprinttipps_bp.route('/sprinttipps')
def sprinttipps():
    return render_template('sprinttipps.html')

@sprinttipps_bp.route('/get_sprinttipps')
def get_sprinttipps():
    name = request.args.get('name')
    city = request.args.get('city')

    db = get_db()
    cursor = db.cursor()

    # 1. user_id anhand des Namens finden
    cursor.execute('SELECT id FROM Users WHERE name = ?', (name,))
    user_result = cursor.fetchone()
    if not user_result:
        drivers = {f'sdriver{i + 1}': "" for i in range(8)}
        return jsonify(drivers)
        #return jsonify({'success': False, 'message': 'User not found'}), 400
    user_id = user_result[0]

    # 2. race_id anhand der Stadt finden
    cursor.execute('SELECT id FROM Races WHERE city = ?', (city,))
    race_result = cursor.fetchone()
    if not race_result:
        drivers = {f'sdriver{i + 1}': "" for i in range(8)}
        return jsonify(drivers)
        #return jsonify({'success': False, 'message': 'Race not found'}), 400
    race_id = race_result[0]

    # 3. Qualifying-Tipps aus der QualiTips-Tabelle auslesen
    cursor.execute("""
           SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8
           FROM SprintTips
           WHERE user_id = ? AND race_id = ?
           ORDER BY id DESC LIMIT 1
       """, (user_id, race_id))
    result = cursor.fetchone()


    if result:
        # Dynamisch Fahrer in ein Dictionary packen
        drivers = {f'sdriver{i+1}': result[i] for i in range(len(result))}
    else:
        # Dynamisch leere Fahrer zurückgeben
        drivers = {f'sdriver{i + 1}': "" for i in range(8)}

    return jsonify(drivers)

@sprinttipps_bp.route('/save_sprinttipps', methods=['POST'])
def save_sprinttipps():
    data = request.get_json()
    name = data['name']
    city = data['city']

    # Race Fahrer 1-3 auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    drivers = [data.get(f'sdriver{i + 1}', '') for i in range(8)]

    db = get_db()
    cursor = db.cursor()

    # 1. user_id ermitteln
    cursor.execute('SELECT id FROM Users WHERE name = ?', (name,))
    user_result = cursor.fetchone()
    if not user_result:
        return jsonify({'success': False, 'message': 'User not found'}), 400
    user_id = user_result[0]

    # 2. race_id ermitteln
    cursor.execute('SELECT id FROM Races WHERE city = ?', (city,))
    race_result = cursor.fetchone()
    if not race_result:
        return jsonify({'success': False, 'message': 'Race not found'}), 400
    race_id = race_result[0]

    # 3. Daten in QualiTips speichern
    cursor.execute('''
            INSERT INTO SprintTips (user_id, race_id, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, race_id, *drivers))

    db.commit()

    return jsonify({'success': True})
