import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, jsonify, session, app
from flask_login import login_required, current_user

from models import utils
from models.db import get_db

# Erstellen des Blueprints
wmStand_bp = Blueprint('wmStand', __name__)

# Registrieren von Routen bei dem Blueprint
@wmStand_bp.route('/wmStand')
def wmstand():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT revent.city
        FROM races r
        JOIN race_events revent ON r.race_event_id = revent.id
        JOIN rennergebnisse re ON r.id = re.race_id
        ORDER BY re.id DESC
        LIMIT 1;
    """)

    rennen = cursor.fetchone()

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
            tipprunde_id=None,
            rennen = rennen
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
                            tipprunde_id=tipprunde_id,
                            rennen = rennen
                           )


@wmStand_bp.route('/wmStand_get_cities', methods=['GET'])
@login_required
def get_cities():
    saison = app.current_app.config['SAISON']
    cities = utils.get_cities(saison)
    rennliste = [f"{name.upper() if details['is_sprint'] else name}, {details['datum']}" for name, details in
                 cities.items()]
    return jsonify(rennliste)

@wmStand_bp.route('/wmStand_get_drivers', methods=['GET'])
def get_drivers():
    saison = app.current_app.config['SAISON']
    return jsonify(utils.get_drivers(saison))


@wmStand_bp.route('/get_wm_stand')
def get_wm_stand():

    city = request.args.get('rennen')
    saison = app.current_app.config['SAISON']

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return {}
    else:
        race_id = race_id['race_id']

    ergebnis = {}
    drivers, success = utils.get_wm_stand(race_id, saison)
    #ergebnis.update(wmdrivers)
    #ergebnis.update(success)

    return jsonify({
        "success": True,
        "message": "Ok",
        "wm_stand": drivers
    })



@wmStand_bp.route('/get_team_stand', methods=['GET'])
def get_team_stand():

    city = request.args.get('rennen')
    saison = app.current_app.config['SAISON']

    race = utils.get_raceID(city, saison)
    if not race['success']:
        return jsonify({"success": False})

    team_wm = utils.get_team_stand(race['race_id'], saison)

    return jsonify({
        "success": True,
        "team_wm": team_wm
    })