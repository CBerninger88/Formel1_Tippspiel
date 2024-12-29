from flask import Blueprint, render_template, request, jsonify
from db import get_db

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('home.html')

@home_bp.route('/get_tipps')
def get_tipps():
    city = request.args.get('city')
    db = get_db()
    cursor = db.cursor()

    ergebnis = {}

    cursor.execute(f'''
         WITH LatestEntries AS (
            SELECT name, driver1, driver2, driver3,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY id DESC) as rn
            FROM tippdata
            WHERE city = ?
        )
        SELECT name, driver1, driver2, driver3
        FROM LatestEntries
        WHERE rn = 1;
        ''', (city,))

    results = cursor.fetchall()

    for result in results:
        name, driver1, driver2, driver3 = result
        if name not in ergebnis:
            ergebnis[name] = []
        ergebnis[name].append((driver1, driver2, driver3))

    return jsonify(ergebnis)
