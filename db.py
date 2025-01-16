from flask import g
import sqlite3


DATABASE = 'tippdata.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection(exception):
    db = getattr(g, 'database', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Users
        cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )''')

        # Races
        cursor.execute('''CREATE TABLE IF NOT EXISTS Races (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    date DATE NOT NULL,
                    is_sprint BOOLEAN DEFAULT 0
                )''')

        # QualiTips
        cursor.execute('''CREATE TABLE IF NOT EXISTS QualiTips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    race_id INTEGER NOT NULL,
                    driver1 TEXT NOT NULL,
                    driver2 TEXT NOT NULL,
                    driver3 TEXT NOT NULL,
                    driver4 TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(id),
                    FOREIGN KEY (race_id) REFERENCES Races(id)
                )''')

        # RaceTips
        cursor.execute('''CREATE TABLE IF NOT EXISTS RaceTips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    race_id INTEGER NOT NULL,
                    driver1 TEXT NOT NULL,
                    driver2 TEXT NOT NULL,
                    driver3 TEXT NOT NULL,
                    driver4 TEXT NOT NULL,
                    driver5 TEXT NOT NULL,
                    driver6 TEXT NOT NULL,
                    driver7 TEXT NOT NULL,
                    driver8 TEXT NOT NULL,
                    driver9 TEXT NOT NULL,
                    driver10 TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(id),
                    FOREIGN KEY (race_id) REFERENCES Races(id)
                )''')

        # SprintTips
        cursor.execute('''CREATE TABLE IF NOT EXISTS SprintTips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    race_id INTEGER NOT NULL,
                    driver1 TEXT NOT NULL,
                    driver2 TEXT NOT NULL,
                    driver3 TEXT NOT NULL,
                    driver4 TEXT NOT NULL,
                    driver5 TEXT NOT NULL,
                    driver6 TEXT NOT NULL,
                    driver7 TEXT NOT NULL,
                    driver8 TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(id),
                    FOREIGN KEY (race_id) REFERENCES Races(id)
                )''')

        # Fastest Lab
        cursor.execute('''CREATE TABLE IF NOT EXISTS FastestLab (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    race_id INTEGER NOT NULL,
                    driver1 TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(id),
                    FOREIGN KEY (race_id) REFERENCES Races(id)
                )''')

        db.commit()