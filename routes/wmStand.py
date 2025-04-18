from flask import Blueprint, render_template, request, jsonify

import utils
from city import City

# Erstellen des Blueprints
wmStand_bp = Blueprint('wmStand', __name__)

# Registrieren von Routen bei dem Blueprint
@wmStand_bp.route('/wmStand')
def wmstand():
    return render_template('wmStand.html')

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