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
    cursor.execute("""
            SELECT driver1, driver2, driver3 FROM tippdata
            WHERE city = ? AND name = ?
            ORDER BY id DESC LIMIT 1
        """, (city, name))
    result = cursor.fetchone()

    if result:
        drivers = {f'driver{i+1}': result[i] for i in range(len(result))}
#        driver1, driver2, driver3 = result
        return jsonify(drivers)
    else:
        # Dynamisch leere Fahrer zurückgeben
        return jsonify({f'driver{i + 1}': 'Fahrer auswählen' for i in range(4)})

@tippabgabe_bp.route('/save_selection', methods=['POST'])
def save_selection():
    data = request.get_json()
    city = data['city']
    name = data['name']

    drivers = [data.get(f'driver{i+1}', '') for i in range(3)]
    values = [name, city] + drivers

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO tippdata (name, city, driver1, driver2, driver3)
        VALUES (?,?,?,?,?)    
    ''', values
    )
    db.commit()

    return jsonify({'success': True})
