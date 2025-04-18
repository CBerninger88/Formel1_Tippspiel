from flask import Blueprint, render_template, request, jsonify

from city import City
import utils
from spieler import Spieler

# Erstellen des Blueprints
rennergebnis_bp = Blueprint('rennergebnis', __name__)

# Registrieren von Routen bei dem Blueprint
@rennergebnis_bp.route('/rennergebnis')
def rennergebnis():
    return render_template('rennergebnis.html')


@rennergebnis_bp.route('/get_cities', methods=['GET'])
def get_cities():
    cities = utils.get_cities()
    rennliste = [f"{name.upper() if details['is_sprint'] else name}, {details['datum']}" for name, details in
                 cities.items()]
    return jsonify(rennliste)


@rennergebnis_bp.route('/get_users_rennergebnis', methods=['GET'])
def get_users():
    return jsonify(utils.get_users())


@rennergebnis_bp.route('/get_einzeltipps')
def get_einzeltipps():
    city = request.args.get('city').split(', ')[0].capitalize()
    name = request.args.get('name')

    race_id = utils.get_raceID(city)
    if not race_id['success']:
        return race_id
    else:
        race_id = race_id['race_id']

    spieler = Spieler(name)
    spielertipps = spieler.get_quali_tipps(race_id)[0]
    spielertipps.update(spieler.get_race_tipps(race_id)[0])
    spielertipps.update(spieler.get_fastestlab_tipp(race_id)[0])
    ergebnis = Spieler('Ergebnis')
    ergebnistipps = ergebnis.get_quali_tipps(race_id)[0]
    ergebnistipps.update(ergebnis.get_race_tipps(race_id)[0])
    ergebnistipps.update(ergebnis.get_fastestlab_tipp(race_id)[0])
    tipppunkte = spieler.get_tipppunkte(race_id)


    ergebnis = {name: spielertipps, 'Ergebnis': ergebnistipps, 'punkte': tipppunkte}

    return jsonify(ergebnis)


@rennergebnis_bp.route('/get_punkte', methods=['POST'])
def get_punkte():
    data = request.get_json()
    city_name = data.get('city').split(', ')[0].capitalize()
    calcNew = data.get('calcNew')

    # Stadt initalisieren
    city = City(city_name)

    # 2. Existiert race_id in der tipppunkte Tabelle
    exists = city.is_tipppunkte()

    if exists and not calcNew:

        tipppunkte, gesamtpunkte, status = city.get_tipppunkte(False)
        ergebnis_sorted = sorted(gesamtpunkte.items(), key=lambda item: item[1]['gesamtPunkte'], reverse=True)

        return jsonify({'punkte': ergebnis_sorted, 'status': status})

    else:
        tipppunkte, gesamtpunkte, status = city.get_tipppunkte(True)
        ergebnis_sorted = sorted(gesamtpunkte.items(), key=lambda item: item[1]['gesamtPunkte'], reverse=True)
        if status['success']:
            city.set_tipppunkte(tipppunkte)

    return jsonify({'punkte': ergebnis_sorted, 'status': status})


