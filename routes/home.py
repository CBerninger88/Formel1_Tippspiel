from flask import Blueprint, render_template, request, jsonify

import utils
from db import get_db
from spieler import Spieler

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('home.html')

@home_bp.route('/get_tipps')
def get_tipps():
    city = request.args.get('city').split(', ')[0].capitalize()
    race_id = utils.get_raceID(city)
    if not race_id['success']:
        return race_id
    else:
        race_id = race_id['race_id']
    ergebnis = {}

    # Get all Quali Tipps
    names = utils.get_tipper(race_id, 'qualitipps')
    for name in names:
        spieler = Spieler(name)
        qualitipps = spieler.get_quali_tipps(race_id)
        if name not in ergebnis:
            ergebnis[name] = {}
        ergebnis[name].update(qualitipps)

    # Get all Race Tipps
    names = utils.get_tipper(race_id, 'racetipps')
    for name in names:
        spieler = Spieler(name)
        racetipps = spieler.get_race_tipps(race_id)
        if name not in ergebnis:
            ergebnis[name] = {}
        ergebnis[name].update(racetipps)

    # Get fastest Lab Tipp
    names = utils.get_tipper(race_id, 'fastestlab')
    for name in names:
        spieler = Spieler(name)
        fastestLabtipp = spieler.get_fastestlab_tipp(race_id)
        if name not in ergebnis:
            ergebnis[name] = {}
        ergebnis[name].update(fastestLabtipp)


    # Get Sprint Tipps if city has Sprintrennen
    is_sprint = utils.is_sprint(city)
    if is_sprint:

        names = utils.get_tipper(race_id, 'sprinttipps')
        for name in names:
            spieler = Spieler(name)
            sprinttipps = spieler.get_sprint_tipps(race_id)
            if name not in ergebnis:
                ergebnis[name] = {}
            ergebnis[name].update(sprinttipps)

        ergebnis.update({f'sprint': is_sprint})

    else:
        ergebnis.update({f'sprint': is_sprint})

    return jsonify(ergebnis)


@home_bp.route('/get_cities', methods=['GET'])
def get_cities():
    return utils.get_cities()
