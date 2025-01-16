from flask import Blueprint, render_template, request, jsonify
from db import get_db

# Erstellen des Blueprints
tippabgabe_bp = Blueprint('tippabgabe', __name__)

# Registrieren von Routen bei dem Blueprint
@tippabgabe_bp.route('/tippabgabe')
def tippabgabe():
    return render_template('tippabgabe.html')

@tippabgabe_bp.route('/get_selection')
def get_selection():
    name = request.args.get('name')
    city = request.args.get('city')

    db = get_db()
    cursor = db.cursor()

    # 1. user_id anhand des Namens finden
    cursor.execute('SELECT id FROM Users WHERE name = ?', (name,))
    user_result = cursor.fetchone()
    if not user_result:
        drivers = {f'qdriver{i + 1}': "" for i in range(4)}
        drivers.update({f'driver{i + 1}': "" for i in range(3)})
        drivers.update({f'fdriver': ""})
        return jsonify(drivers)
        #return jsonify({'success': False, 'message': 'User not found'}), 400
    user_id = user_result[0]

    # 2. race_id anhand der Stadt finden
    cursor.execute('SELECT id FROM Races WHERE city = ?', (city,))
    race_result = cursor.fetchone()
    if not race_result:
        drivers = {f'qdriver{i + 1}': "" for i in range(4)}
        drivers.update({f'driver{i + 1}': "" for i in range(3)})
        drivers.update({f'fdriver': ""})
        return jsonify(drivers)
        #return jsonify({'success': False, 'message': 'Race not found'}), 400
    race_id = race_result[0]

    # 3. Qualifying-Tipps aus der QualiTips-Tabelle auslesen
    cursor.execute("""
           SELECT driver1, driver2, driver3, driver4
           FROM QualiTips
           WHERE user_id = ? AND race_id = ?
           ORDER BY id DESC LIMIT 1
       """, (user_id, race_id))
    qresult = cursor.fetchone()

    # 4. Race-Tipps aus der RaceTips-Tabelle auslesen
    cursor.execute("""
               SELECT driver1, driver2, driver3
               FROM RaceTips
               WHERE user_id = ? AND race_id = ?
               ORDER BY id DESC LIMIT 1
           """, (user_id, race_id))
    result = cursor.fetchone()

    # 4. Fastest Driver aus der FastestLab-Tabelle auslesen
    cursor.execute("""
                 SELECT driver1
                 FROM FastestLab
                 WHERE user_id = ? AND race_id = ?
                 ORDER BY id DESC LIMIT 1
             """, (user_id, race_id))
    fresult = cursor.fetchone()

    if qresult:
        # Dynamisch Fahrer in ein Dictionary packen
        drivers = {f'qdriver{i+1}': qresult[i] for i in range(len(qresult))}
    else:
        # Dynamisch leere Fahrer zurückgeben
        drivers = {f'qdriver{i + 1}': "" for i in range(4)}

    if result:
        # Dynamisch Fahrer in ein Dictionary packen
        drivers.update({f'driver{i+1}': result[i] for i in range(len(result))})
    else:
        # Dynamisch leere Fahrer zurückgeben
        drivers.update({f'driver{i+1}': "" for i in range(3)})

    if fresult:
        # Dynamisch Fahrer in ein Dictionary packen
        drivers.update({f'fdriver': fresult[0]})
    else:
        # Dynamisch leere Fahrer zurückgeben
        drivers.update({f'fdriver': ""})


    return jsonify(drivers)

@tippabgabe_bp.route('/save_selection', methods=['POST'])
def save_selection():
    data = request.get_json()
    name = data['name']
    city = data['city']

    # Quali Fahrer 1-4 auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    qdrivers = [data.get(f'qdriver{i+1}', '') for i in range(4)]

    # Race Fahrer 1-3 auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    drivers = [data.get(f'driver{i + 1}', '') for i in range(3)]

    # Schnellsten Fahrer auslesen
    fdriver = data.get(f'fDriver', '')

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
            INSERT INTO QualiTips (user_id, race_id, driver1, driver2, driver3, driver4)
            VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, race_id, *qdrivers))

    # 3. Daten in RaceTips speichern
    cursor.execute('''
                INSERT INTO RaceTips (user_id, race_id, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10 )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, race_id, *drivers, '', '', '', '', '', '', ''))

    # 3. Daten in FastestLab speichern
    cursor.execute('''
                   INSERT INTO FastestLab (user_id, race_id, driver1)
                   VALUES (?, ?, ?)
           ''', (user_id, race_id, fdriver))

    db.commit()

    return jsonify({'success': True})
