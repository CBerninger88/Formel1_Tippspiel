import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import current_user

import utils
from city import City
from db import get_db

# Erstellen des Blueprints
wmStand_bp = Blueprint('wmStand', __name__)

# Registrieren von Routen bei dem Blueprint
@wmStand_bp.route('/wmStand')
def wmstand():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # 🔹 Tipprunden des aktuellen Users
    cursor.execute("""
                    SELECT t.id, t.name
                    FROM tipprunden t
                    JOIN tipprunden_user tu ON tu.tipprunde_id = t.id
                    WHERE tu.user_id = %s
                    ORDER BY t.name
                """, (current_user.id,))
    tipprunden = cursor.fetchall()

    # 🔹 Fall: User ist in keiner Tipprunde
    if not tipprunden:
        return render_template(
            "wmStand.html",
            tipprunden=[],
            users=[current_user],
            tipprunde_id=None
        )

    # 🔹 Fallback: erste Tipprunde
    tipprunde_id = session.get('tipprunde_id') or tipprunden[0]['id']

    # 🔹 User der aktiven Tipprunde
    cursor.execute("""
                    SELECT u.id, u.username
                    FROM users u
                    JOIN tipprunden_user tu ON tu.user_id = u.id
                    WHERE tu.tipprunde_id = %s
                    ORDER BY u.username
                """, (tipprunde_id,))
    users = cursor.fetchall()

    return render_template("wmStand.html",
                           tipprunden=tipprunden,
                           users=users,
                           tipprunde_id=tipprunde_id
                           )

@wmStand_bp.route('/wmStand_get_cities', methods=['GET'])
def get_cities():
    cities = utils.get_cities()
    rennliste = [f"{name.upper() if details['is_sprint'] else name}, {details['datum']}" for name, details in
                 cities.items()]
    return jsonify(rennliste)

@wmStand_bp.route('/wmStand_get_drivers', methods=['GET'])
def get_drivers():
    return jsonify(utils.get_drivers())


@wmStand_bp.route('/get_wm_stand')
def get_wm_stand():

    cityName = request.args.get('city').split(', ')[0].capitalize()

    city = City(cityName)
    ergebnis = {}
    wmdrivers, success = city.get_wm_stand()
    ergebnis.update(wmdrivers)
    ergebnis.update(success)

    return jsonify(ergebnis)



@wmStand_bp.route('/save_wm_stand', methods=['POST'])
def save_wm_stand():

    data = request.get_json()
    cityName = data['city'].split(', ')[0].capitalize()

    # WM Stand auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    wmStand = [data.get(f'wmdriver{i + 1}', '') for i in range(20)]

    city = City(cityName)

    city.set_wm_stand(wmStand)


    return jsonify({'success': True})