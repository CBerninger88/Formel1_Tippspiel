from flask import Blueprint, render_template, request, jsonify, app
from flask_login import login_required
from models.decorator import admin_required
from models import utils

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/rennergebnisse")
@login_required
@admin_required
def rennergebnisse():
    return render_template("admin/rennergebnisse.html")

@admin_bp.route("/sprintergebnisse")
@login_required
@admin_required
def sprintergebnisse():
    return render_template("admin/sprintergebnisse.html")


@admin_bp.route("/get_rennergebnis")
@login_required
@admin_required
def get_rennergebnis():
    #name = current_user.username
    city = request.args.get('city').split(', ')[0].capitalize()
    #tipprunde_id = request.args.get('tipprunde_id')
    saison = app.current_app.config['SAISON']

    #if tipprunde_id is None:
    #    tipprunde_id = 0

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return {}
    else:
        race_id = race_id['race_id']

    qdrivers, quali_status = utils.get_qualiergebnis([race_id], saison)
    rdrivers, race_status = utils.get_rennergebnis([race_id], saison)
    fdriver, fastestlap_status = utils.get_fastestlap_ergebnis([race_id], saison)

    ergebnis = {}
    ergebnis.update(qdrivers.get(race_id, {}))
    ergebnis.update(rdrivers.get(race_id, {}))
    ergebnis.update(fdriver.get(race_id, {}))
    ergebnis.update(race_status)

    return jsonify(ergebnis)

@admin_bp.route("/get_sprintergebnis")
@login_required
@admin_required
def get_sprintergebnis():
    #name = current_user.username
    city = request.args.get('city').split(', ')[0].capitalize()
    #tipprunde_id = request.args.get('tipprunde_id')
    saison = app.current_app.config['SAISON']

    #if tipprunde_id is None:
    #    tipprunde_id = 0

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return {}
    else:
        race_id = race_id['race_id']

    ergebnis = {}
    drivers, success = utils.get_sprintergebnis([race_id], saison)
    ergebnis.update(drivers.get(race_id))
    ergebnis.update(success)

    return jsonify(ergebnis)


@admin_bp.route('/save_rennergebnis', methods=['POST'])
@login_required
@admin_required
def save_rennergebnis():
    data = request.get_json()
    city = data['city'].split(', ')[0].capitalize()
    saison = app.current_app.config['SAISON']

    # Quali-Fahrer (1-4), race fahrer (1-10), fastestLab Fahrer auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    qdrivers = [data.get(f'qdriver{i + 1}', '') for i in range(4)]
    rdrivers = [data.get(f'driver{i + 1}', '') for i in range(22)]
    fdriver = [data.get(f'fdriver', '')]

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return race_id
    else:
        race_id = race_id['race_id']

    utils.set_qualiergebnis(race_id, saison, qdrivers)
    utils.set_rennergebnis(race_id, saison, rdrivers)
    utils.set_fastestlap_ergebnis(race_id, saison, fdriver)

    utils.set_dummies(race_id, saison, qdrivers, rdrivers, fdriver)

    return jsonify({'success': True})


@admin_bp.route('/save_sprintergebnis', methods=['POST'])
@login_required
@admin_required
def save_sprintergebnis():
    data = request.get_json()
    city = data['city'].split(', ')[0].capitalize()
    saison = app.current_app.config['SAISON']

    # Quali-Fahrer (1-4), race fahrer (1-10), fastestLab Fahrer auslesen (Standardwert ist ein leerer String, falls nicht übergeben)
    drivers = [data.get(f'driver{i+1}', '') for i in range(8)]

    race_id = utils.get_raceID(city, saison)
    if not race_id['success']:
        return race_id
    else:
        race_id = race_id['race_id']

    utils.set_sprintergebnis(race_id, saison, drivers)

    return jsonify({'success': True})


@admin_bp.route('/rennergebnis_get_cities', methods=['GET'])
@login_required
@admin_required
def get_cities():
    saison = app.current_app.config['SAISON']
    cities = utils.get_cities(saison)
    rennliste = [f"{name.upper() if details['is_sprint'] else name}, {details['datum']}" for name, details in
                 cities.items()]
    return jsonify(rennliste)

@admin_bp.route('/sprintergebnis_get_cities', methods=['GET'])
@login_required
@admin_required
def get_sprintCities():
    saison = app.current_app.config['SAISON']
    cities = utils.get_sprintCities(saison)
    rennliste = [f"{name.upper() if details['is_sprint'] else name}, {details['datum']}" for name, details in
                 cities.items()]
    return jsonify(rennliste)



@admin_bp.route('/rennergebnis_get_drivers', methods=['GET'])
@login_required
@admin_required
def get_drivers():
    saison = app.current_app.config['SAISON']
    return jsonify(utils.get_drivers(saison))

@admin_bp.route("/races")
@login_required
@admin_required
def races():
    return render_template("admin/races.html")


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    return render_template("admin/users.html")


