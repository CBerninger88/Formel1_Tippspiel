import os
import psycopg2
from flask import g


#DATABASE = 'tippdata.db'

def get_db():
    #db = getattr(g, '_database', None)
    if 'db' not in g:
        g.db = psycopg2.connect("postgresql://tippdatenbank_user:TnbFCl4BR2ZK9fWQRtD481XdSs6EjQXL@dpg-cu555a5ds78s73dvrot0-a.frankfurt-postgres.render.com/tippdatenbank")
    return g.db

def close_connection(exception):
    db = getattr(g, 'database', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Users
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )''')

        # Races
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS races (
                id SERIAL PRIMARY KEY,
                city TEXT NOT NULL,
                date DATE NOT NULL,
                is_sprint BOOLEAN DEFAULT FALSE
            );
        ''')

        # QualiTips
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qualitipps (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                race_id INTEGER REFERENCES races(id),
                driver1 TEXT NOT NULL,
                driver2 TEXT NOT NULL,
                driver3 TEXT NOT NULL,
                driver4 TEXT NOT NULL
            );
        ''')

        # RaceTips
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS racetipps (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES Users(id),
                race_id INTEGER REFERENCES Races(id),
                driver1 TEXT NOT NULL,
                driver2 TEXT NOT NULL,
                driver3 TEXT NOT NULL,
                driver4 TEXT NOT NULL,
                driver5 TEXT NOT NULL,
                driver6 TEXT NOT NULL,
                driver7 TEXT NOT NULL,
                driver8 TEXT NOT NULL,
                driver9 TEXT NOT NULL,
                driver10 TEXT NOT NULL
            );
        ''')

        # SprintTips
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SprintTips (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                race_id INTEGER REFERENCES races(id),
                driver1 TEXT NOT NULL,
                driver2 TEXT NOT NULL,
                driver3 TEXT NOT NULL,
                driver4 TEXT NOT NULL,
                driver5 TEXT NOT NULL,
                driver6 TEXT NOT NULL,
                driver7 TEXT NOT NULL,
                driver8 TEXT NOT NULL
            );
        ''')

        # Fastest Lab
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fastestlab (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                race_id INTEGER REFERENCES races(id),
                driver1 TEXT NOT NULL
            );
        ''')

        db.commit()