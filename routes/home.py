from flask import Blueprint, render_template, request, jsonify
from db import get_db

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('home.html')

@home_bp.route('/get_tipps')
def get_tipps():
    city = request.args.get('city').split(', ')[0]
    db = get_db()
    cursor = db.cursor()

    # 2. race_id ermitteln
    cursor.execute('SELECT id FROM races WHERE city = %s', (city,))
    race_result = cursor.fetchone()
    if not race_result:
        return jsonify({'success': False, 'message': 'Race not found'}), 400
    race_id = race_result[0]

    ergebnis = {}

    cursor.execute(f'''
         WITH LatestEntries AS (
            SELECT q.user_id, q.driver1, q.driver2, q.driver3, q.driver4,
                ROW_NUMBER() OVER (PARTITION BY q.user_id ORDER BY q.id DESC) as rn
            FROM qualitipps q
            WHERE q.race_id = %s
        )
        SELECT u.name, q.driver1, q.driver2, q.driver3, q.driver4
        FROM LatestEntries q
        JOIN users u ON u.id = q.user_id
        WHERE rn = 1;
        ''', (race_id,))

    qresults = cursor.fetchall()

    cursor.execute(f'''
             WITH LatestEntries AS (
                SELECT r.user_id, r.driver1, r.driver2, r.driver3, r.driver4, r.driver5, r.driver6, r.driver7, r.driver8, r.driver9, r.driver10,
                    ROW_NUMBER() OVER (PARTITION BY r.user_id ORDER BY r.id DESC) as rn
                FROM racetipps r
                WHERE r.race_id = %s
            )
            SELECT u.name, r.driver1, r.driver2, r.driver3, r.driver4, r.driver5, r.driver6, r.driver7, r.driver8, r.driver9, r.driver10
            FROM LatestEntries r
            JOIN users u ON u.id = r.user_id
            WHERE rn = 1;
            ''', (race_id,))

    rresults = cursor.fetchall()

    cursor.execute(f'''
                 WITH LatestEntries AS (
                    SELECT f.user_id, f.driver1,
                        ROW_NUMBER() OVER (PARTITION BY f.user_id ORDER BY f.id DESC) as rn
                    FROM fastestlab f
                    WHERE f.race_id = %s
                )
                SELECT u.name, f.driver1
                FROM LatestEntries f
                JOIN users u ON u.id = f.user_id
                WHERE rn = 1;
                ''', (race_id,))

    fresults = cursor.fetchall()

    for qresult in qresults:
        name, driver1, driver2, driver3, driver4 = qresult
        if name not in ergebnis:
            ergebnis[name] = {}
        ergebnis[name].update({f'qdriver{i+1}': qresult[i+1] for i in range(len(qresult)-1)})#, 'qdriver2': driver2, 'qdriver3': driver3, 'qdriver4': driver4})

    for rresult in rresults:
        name = rresult[0]
        if name not in ergebnis:
            ergebnis[name] = {}
        ergebnis[name].update({f'rdriver{i+1}': rresult[i+1] for i in range(len(rresult)-1)})

    for fresult in fresults:
        name = fresult[0]
        if name not in ergebnis:
            ergebnis[name] = {}
        ergebnis[name].update({f'fdriver': fresult[1]})


    return jsonify(ergebnis)


@home_bp.route('/get_cities', methods=['GET'])
def get_cities():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT city, date FROM races ORDER BY date ASC;")
    result = cursor.fetchall()

    # Liste der Städte extrahieren
    cities = [f'{row[0]}, {row[1]}' for row in result]

    return jsonify(cities)
