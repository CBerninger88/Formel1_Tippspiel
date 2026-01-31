import psycopg2
from flask_login import current_user, login_required
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, jsonify, session, app, request

import utils
from datetime import date
from datetime import datetime

from db import get_db
from models.dummy import Dummytipps
from spieler import Spieler

# Erstellen des Blueprints
gesamtergebnis_bp = Blueprint('gesamtergebnis', __name__)

# Registrieren von Routen bei dem Blueprint
@gesamtergebnis_bp.route('/gesamtergebnis')
def gesamtnergebnis():
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
            "gesamtergebnis.html",
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

    return render_template("gesamtergebnis.html",
                           tipprunden=tipprunden,
                           users=users,
                           tipprunde_id=tipprunde_id
                           )

@gesamtergebnis_bp.route('/get_gesamtpunkte')
@login_required
def get_gesamtpunkte():
    saison = app.current_app.config['SAISON']
    tipprunde_id = request.args.get('tipprunde_id', saison)
    spieler = utils.get_users_in_tipprunde(tipprunde_id)
    heute = date(2026, 3, 26)#date.today()
    stichtag = datetime(2025, 3, 20)
    cities = utils.get_cities(saison)

    gefilterte_rennen = {
        name: details
        for name, details in cities.items()
        if details["datum"] <= heute
    }

    return jsonify({"players": [{ "username": "Christoph", "points": 120 }, { "username": "Simon", "points": 98 }]})

    ergebnis = {}
    for user in spieler:
        name = user['username']
        if name == "Ergebnis" or name in app.current_app.config['DUMMIES']:
            continue
        gesamtpunkte = 0
        for rennen in gefilterte_rennen:
            tippunkte = Spieler(name).get_tipppunkte(gefilterte_rennen[rennen]['race_id'])
            gesamtpunkte += sum(tippunkte.values())
        ergebnis[name] = gesamtpunkte

    ergebnis_sorted = sorted(ergebnis.items(), key=lambda item: item[1], reverse=True)


    status = {'success': True, 'message': 'Alles ok'}

    return jsonify({'spieler': ergebnis_sorted, 'status': status})

@gesamtergebnis_bp.route('/get_racepunkte')
@login_required
def get_racepunkte():

    tipprunde_id = request.args.get('tipprunde_id')
    city = request.args.get('city').split(', ')[0].capitalize()

    saison = app.current_app.config['SAISON']
    spieler = utils.get_users_in_tipprunde(tipprunde_id)
    heute = date(2026, 3, 26)  # date.today()

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return {}
    else:
        race_id = race_id['race_id']

    # Qualiergebnis einmal abziehen
    qualiergebnis, status1 = utils.get_qualiergebnis(race_id, saison)
    raceergebnis, status2 = utils.get_rennergebnis(race_id, saison)
    fastestlapergebnis, status3 = utils.get_fastestlap_ergebnis(race_id, saison)
    if not status1['success'] or not status2['success'] or not status3['success']:
        success = False
        message = f'Es gibt für {city} noch kein Rennergebnis'
        return {"success": False, "message": message, "players": []}

    # WM Stand einmal abziehen
    wmStand, status = utils.get_wm_stand(race_id, saison)
    if not wmStand:
        success = False
        message = f'Es gibt für {city} noch keinen WM Stand'
        return {"success": False, "message": message, "players": []}

    players = []
    for user in spieler:
        user_id = user['id']
        if user['username'] == "Ergebnis":
            continue

        # Qualitipps für user abziehen
        if user['username'] in app.current_app.config['DUMMIES']:
            dummy_service = Dummytipps()
            qualitipps = dummy_service.get_tipps(user_id, race_id, saison, 'quali')
            racetipps = dummy_service.get_tipps(user_id, race_id, saison, 'race')
            fastestlaptipp = dummy_service.get_tipps(user_id, race_id, saison, 'fastest')
            qpunkte, _, _ = utils.get_qualipunkte(qualiergebnis, qualitipps)
            rpunkte, _, _ = utils.get_racepunkte(raceergebnis, racetipps, wmStand, city)
            fpunkte, _, _ = utils.get_fastestlappunkte(fastestlapergebnis, fastestlaptipp)
        else:
            player = Spieler(user['username'])
            qualitipps, status1 = player.get_quali_tipps(race_id, tipprunde_id)
            racetipps, status2 = player.get_race_tipps(race_id, tipprunde_id)
            fastestlaptipp, status3 = player.get_fastestlab_tipp(race_id, tipprunde_id)
            if not status1['success'] or not status2['success'] or not status3['success']:
                success = False
                message = f'Es gibt für {user['username']} kein vollständigen-Tipp'
                qpunkte = 0
                rpunkte = 0
                fpunkte = 0
            else:
                qpunkte, _, _ = utils.get_qualipunkte(qualiergebnis, qualitipps)
                rpunkte, _, _ = utils.get_racepunkte(raceergebnis, racetipps, wmStand, city)
                fpunkte, _, _ = utils.get_fastestlappunkte(fastestlapergebnis, fastestlaptipp)

        gesamtpunkte = qpunkte + rpunkte + fpunkte
        points = {'quali': qpunkte, 'race': rpunkte, 'fastestlap': fpunkte, 'total': gesamtpunkte }
        players.append({'username': user['username'], 'points': points})

    players_sorted = sorted(
        players,
        key=lambda x: int(x["points"]["total"]),
        reverse=True
    )

    ergebnis = {"success": True, "players": players_sorted}

    return jsonify(ergebnis)