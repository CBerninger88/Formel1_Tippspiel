from flask import Flask, request, jsonify, render_template, g
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'tippdata.db'

names = ['Christoph', 'Christine']
drivers = ['driver1', 'driver2']

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tippdata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                driver1 TEXT NOT NULL,
                driver2 TEXT NOT NULL
            )
        ''')
        db.commit()


# Speichert die Auswahlen
#tippData = {
#    "Christine": {},
#    "Christoph": {}
#}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tabelle')
def tabelle():
    return render_template('tabelle.html')

@app.route('/tippabgabe')
def tippabgabe():
    return render_template('tippabgabe.html')

@app.route('/get_selection')
def get_selection():
    name = request.args.get('name')
    city = request.args.get('city')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
            SELECT driver1, driver2 FROM tippdata
            WHERE city = ? AND name = ?
            ORDER BY id DESC LIMIT 1
        """, (city, name))
    result = cursor.fetchone()

    if result:
        driver1, driver2 = result
        return jsonify({'driver1': driver1, 'driver2': driver2})
    else:
        return jsonify({'driver1': '', 'driver2': ''})

@app.route('/save_selection', methods=['POST'])
def save_selection():
    data = request.get_json()
    city = data['city']
    name = data['name']
    driver1 = data['driver1']
    driver2 = data['driver2']

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO tippdata (name, city, driver1, driver2)
        VALUES (?,?,?,?)    
    ''', (name, city, driver1, driver2)
    )
    db.commit()

    return jsonify({'success': True})


@app.route('/get_tipps')
def get_tipps():
    city = request.args.get('city')
    #name = 'Christine'
    driver1_list = []
    driver2_list = []
    db = get_db()
    cursor = db.cursor()

    ergebnis = {}

    cursor.execute(f'''
         WITH LatestEntries AS (
            SELECT name, driver1, driver2,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY id DESC) as rn
            FROM tippdata
            WHERE city = ?
        )
        SELECT name, driver1, driver2
        FROM LatestEntries
        WHERE rn = 1;
        ''', (city,))

    results = cursor.fetchall()

    for result in results:
        name, driver1, driver2 = result
        if name not in ergebnis:
            ergebnis[name] = []
        ergebnis[name].append((driver1, driver2))
#    for name in names:
#        cursor.execute('''
#            SELECT driver1, driver2 FROM tippdata
#            WHERE city = ? AND name = ?
#            ORDER BY id DESC LIMIT 1
#            ''', (city, name))
#        result = cursor.fetchone()
#
#        if result is None:
#            ergebnis.append({'name': name, 'driver1': 'Fahrer 1', 'driver2': 'Fahrer 2'})
#        else:
#            driver1, driver2 = result
#            ergebnis.append({'name': name, 'driver1': driver1, 'driver2': driver2})

    return jsonify(ergebnis)




if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    flask_app = os.getenv('FLASK_APP')
    flask_env = os.getenv('FLASK_ENV')
    port = int(os.environ.get('PORT', 5000))
    init_db()
    print(flask_env)
    app.run(host='0.0.0.0', debug=False, port=port)
    test = 1

