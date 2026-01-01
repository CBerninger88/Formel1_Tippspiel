import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect, app
from flask_login import login_required, current_user
from db import get_db

import utils
from spieler import Spieler

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
@home_bp.route("/tipprunde/<int:tipprunde_id>")
@login_required
def index(tipprunde_id=None):
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
            "home.html",
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

    return render_template("home.html",
            tipprunden=tipprunden,
            users=users,
            tipprunde_id=tipprunde_id
    )

@home_bp.route('/get_tipps')
def get_tipps():
    city = request.args.get('city').split(', ')[0].capitalize()
    tipprunde_id = request.args.get('tipprunde_id')
    saison = app.current_app.config['SAISON']

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return race_id
    else:
        race_id = race_id['race_id']

    ergebnis = {}

    # 🔹 Keine Tipprunde → nur current_user
    if not tipprunde_id:
        tipprunde_id = 0
        name = current_user.username
        ergebnis[name] = {}
        spieler = Spieler(name)
        qualitipps = spieler.get_quali_tipps(race_id, tipprunde_id)[0]
        racetipps = spieler.get_race_tipps(race_id, tipprunde_id)[0]
        fastestLabtipp = spieler.get_fastestlab_tipp(race_id, tipprunde_id)[0]

        ergebnis[name].update(qualitipps)
        ergebnis[name].update(racetipps)
        ergebnis[name].update(fastestLabtipp)


        is_sprint = utils.is_sprint(city, saison)
        if is_sprint:
            sprinttipps = spieler.get_sprint_tipps(race_id, tipprunde_id)[0]
            ergebnis[name].update(sprinttipps)

        ergebnis.update({f'sprint': is_sprint})

        return jsonify(ergebnis)

    # Get all Quali Tipps
    names = utils.get_tipper(race_id, tipprunde_id, 'qualitipps')
    for name in names:
        spieler = Spieler(name)
        qualitipps = spieler.get_quali_tipps(race_id, tipprunde_id)[0]
        if name not in ergebnis:
            ergebnis[name] = {}
        ergebnis[name].update(qualitipps)

    # Get all Race Tipps
    names = utils.get_tipper(race_id, tipprunde_id, 'racetipps')
    for name in names:
        spieler = Spieler(name)
        racetipps = spieler.get_race_tipps(race_id, tipprunde_id)[0]
        if name not in ergebnis:
            ergebnis[name] = {}
        ergebnis[name].update(racetipps)

    # Get fastest Lab Tipp
    names = utils.get_tipper(race_id, tipprunde_id,'fastestlab')
    for name in names:
        spieler = Spieler(name)
        fastestLabtipp = spieler.get_fastestlab_tipp(race_id, tipprunde_id)[0]
        if name not in ergebnis:
            ergebnis[name] = {}
        ergebnis[name].update(fastestLabtipp)


    # Get Sprint Tipps if city has Sprintrennen
    is_sprint = utils.is_sprint(city, saison)
    if is_sprint:

        names = utils.get_tipper(race_id, tipprunde_id, 'sprinttipps')
        for name in names:
            spieler = Spieler(name)
            sprinttipps = spieler.get_sprint_tipps(race_id, tipprunde_id)[0]
            if name not in ergebnis:
                ergebnis[name] = {}
            ergebnis[name].update(sprinttipps)

        ergebnis.update({f'sprint': is_sprint})

    else:
        ergebnis.update({f'sprint': is_sprint})

    return jsonify(ergebnis)


@home_bp.route('/get_cities', methods=['GET'])
def get_cities():
    saison = app.current_app.config['SAISON']
    cities = utils.get_cities(saison)
    rennliste = [f"{name.upper() if details['is_sprint'] else name}, {details['datum']}" for name, details in cities.items()]
    return jsonify(rennliste)

@home_bp.route('/get_users', methods=['GET'])
def get_users():
    tipprunde_id = request.args.get('tipprunde_id')
    if tipprunde_id is None:
        return jsonify([current_user.username])
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
            SELECT u.username
            FROM tipprunden_user tu
            JOIN users u ON tu.user_id = u.id
            WHERE tu.tipprunde_id = %s
            ORDER BY u.username
        """, (tipprunde_id,))
    result = cursor.fetchall()
    usernames = [row[0] for row in result]
    return jsonify(usernames)


@home_bp.route("/change_tipprunde/<int:tipprunde_id>")
@login_required
def change_tipprunde(tipprunde_id):
    session['tipprunde_id'] = tipprunde_id
    # Optional: zurück zur Seite, von der der User kam
    next_page = request.args.get('next') or request.referrer or url_for('home.index')
    return redirect(next_page)
