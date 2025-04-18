from flask import Blueprint, render_template, jsonify, request

import utils
from datetime import date
from datetime import datetime

from spieler import Spieler

# Erstellen des Blueprints
gesamtergebnis_bp = Blueprint('gesamtergebnis', __name__)

# Registrieren von Routen bei dem Blueprint
@gesamtergebnis_bp.route('/gesamtergebnis')
def gesamtnergebnis():
    return render_template('gesamtergebnis.html')

@gesamtergebnis_bp.route('/get_gesamtpunkte',  methods=['POST'])
def get_gesamtpunkte():

    spieler = utils.get_users()
    heute = date.today()
    stichtag = datetime(2025, 3, 20)
    cities = utils.get_cities()

    gefilterte_rennen = {
        name: details
        for name, details in cities.items()
        if details["datum"] <= heute
    }

    ergebnis = {}
    for name in spieler:
        if name == "Ergebnis":
            continue
        gesamtpunkte = 0
        for rennen in gefilterte_rennen:
            tippunkte = Spieler(name).get_tipppunkte(gefilterte_rennen[rennen]['race_id'])
            gesamtpunkte += sum(tippunkte.values())
        ergebnis[name] = gesamtpunkte

    ergebnis_sorted = sorted(ergebnis.items(), key=lambda item: item[1], reverse=True)


    status = {'success': True, 'message': 'Alles ok'}

    return jsonify({'spieler': ergebnis_sorted, 'status': status})