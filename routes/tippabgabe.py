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
        driver1, driver2, driver3 = result
        return jsonify({'driver1': driver1, 'driver2': driver2, 'driver3': driver3})
    else:
        return jsonify({'driver1': '', 'driver2': '', 'driver3': ''})

@tippabgabe_bp.route('/save_selection', methods=['POST'])
def save_selection():
    data = request.get_json()
    city = data['city']
    name = data['name']
    driver1 = data['driver1']
    driver2 = data['driver2']
    driver3 = data['driver3']

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO tippdata (name, city, driver1, driver2, driver3)
        VALUES (?,?,?,?,?)    
    ''', (name, city, driver1, driver2, driver3)
    )
    db.commit()

    return jsonify({'success': True})
