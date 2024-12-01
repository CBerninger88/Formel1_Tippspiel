from flask import Flask, request, jsonify, render_template, g
import sqlite3

app = Flask(__name__)

DATABASE = 'tippdata.db'

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
