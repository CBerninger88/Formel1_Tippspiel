from pickle import NEXT_BUFFER

from flask import Blueprint, render_template, request, jsonify
from db import get_db

# Erstellen des Blueprints
rennergebnis_bp = Blueprint('rennergebnis', __name__)

# Registrieren von Routen bei dem Blueprint
@rennergebnis_bp.route('/rennergebnis')
def rennergebnis():
    return render_template('rennergebnis.html')


@rennergebnis_bp.route('/get_cities', methods=['GET'])
def get_cities():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT city, date FROM races ORDER BY date ASC;")
    result = cursor.fetchall()

    # Liste der Städte extrahieren
    cities = [f'{row[0]}, {row[1]}' for row in result]

    return jsonify(cities)


@rennergebnis_bp.route('/get_punkte', methods=['POST'])
def get_punkte():
    data = request.get_json()
    city = data.get('city').split(', ')[0]
    names = data.get('names')

    db = get_db()
    cursor = db.cursor()

    # 2. race_id ermitteln
    cursor.execute('SELECT id FROM races WHERE city = %s', (city,))
    race_result = cursor.fetchone()
    if not race_result:
        return jsonify({'success': False, 'message': 'Race not found'}), 400
    race_id = race_result[0]


    # 3. Qualitipps ermitteln
    cursor.execute(f'''
                 WITH LatestEntries AS (
                    SELECT q.user_id, q.driver1, q.driver2, q.driver3, q.driver4,
                        ROW_NUMBER() OVER (PARTITION BY q.user_id ORDER BY q.id DESC) as rn
                    FROM qualitipps q
                    WHERE q.race_id = %s
                )
                SELECT u.name, r.driver1, r.driver2, r.driver3, r.driver4
                FROM LatestEntries r
                JOIN users u ON u.id = r.user_id
                WHERE rn = 1;
                ''', (race_id,))

    qualitipps = cursor.fetchall()
    qualitipps = {tup[0]: tup[1:] for tup in qualitipps}
    if not qualitipps:
        return jsonify({'success': False, 'message': 'Es wurden noch keine Tipps abgegeben für dieses Rennen'}), 400

    if 'Ergebnis' not in qualitipps:
        return jsonify({'success': False, 'message': 'Es wurden noch keine Ergebnis für dieses Rennen eingetragen'}), 400


    # 3. Racetipps ermitteln
    cursor.execute(f'''
                 WITH LatestEntries AS (
                    SELECT r.user_id, r.driver1, r.driver2, r.driver3, r.driver4, r.driver5, r.driver6, r.driver7, r.driver8, r.driver9, r.driver10,
                        ROW_NUMBER() OVER (PARTITION BY r.user_id ORDER BY r.id DESC) as rn
                    FROM racetipps r
                    WHERE r.race_id = %s
                )
                SELECT u.name, r.driver1, r.driver2, r.driver3, r.driver4, r.driver5, r.driver6, r.driver7, r.driver8, r.driver9, r.driver10
                FROM LatestEntries r
                JOIN users u ON u.id = r.user_id
                WHERE rn = 1;
                ''', (race_id,))

    racetipps = cursor.fetchall()
    racetipps = {tup[0]: tup[1:] for tup in racetipps}
    if not racetipps:
        return jsonify({'success': False, 'message': 'Es wurden noch keine Tipps abgegeben für dieses Rennen'}), 400

    if 'Ergebnis' not in racetipps:
        return jsonify(
            {'success': False, 'message': 'Es wurden noch keine Ergebnis für dieses Rennen eingetragen'}), 400

    # 3. SchnellsteRundeTipp ermitteln
    cursor.execute(f'''
                     WITH LatestEntries AS (
                        SELECT fl.user_id, fl.driver1,
                            ROW_NUMBER() OVER (PARTITION BY fl.user_id ORDER BY fl.id DESC) as rn
                        FROM fastestlab fl
                        WHERE fl.race_id = %s
                    )
                    SELECT u.name, r.driver1
                    FROM LatestEntries r
                    JOIN users u ON u.id = r.user_id
                    WHERE rn = 1;
                    ''', (race_id,))


    fastestlabtipps = cursor.fetchall()
    fastestlabtipps = {tup[0]: tup[1:] for tup in fastestlabtipps}
    if not fastestlabtipps:
        return jsonify({'success': False, 'message': 'Es wurden noch keine Tipps abgegeben für dieses Rennen'}), 400

    if 'Ergebnis' not in fastestlabtipps:
        return jsonify({'success': False, 'message': 'Es wurden noch keine Ergebnis für dieses Rennen eingetragen'}), 400


    # Den WM Stand holen
    cursor.execute("""
               SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10, driver11,
                        driver12, driver13, driver14, driver15, driver16, driver17, driver18, driver19, driver20
               FROM wmstand
               WHERE race_id = %s
               ORDER BY id DESC LIMIT 1
           """, (race_id,))
    wmStand = cursor.fetchone()
    if not wmStand:
        return jsonify({'success': False, 'message': 'Es gibt keinen WM Stand für dieses Rennen'}), 400


    qualiPunkte = calculate_qualipunkte(qualitipps)
    fastestLabPunkte = calculate_fastestLabPunkte(fastestlabtipps)
    racePunkte = calculate_racepunkte(racetipps, wmStand)

    ergebnis = {}
    for name in names:
        gesamtpunkte = 0
        if name in qualiPunkte:
            gesamtpunkte = qualiPunkte[name] + fastestLabPunkte[name] + racePunkte[name]
        ergebnis.update({name: gesamtpunkte})

    #ergebnis = {names[0]: 10, names[1]: 20, names[2]: 30, names[3]: 40, names[4]: 50}

    return jsonify(ergebnis)



def calculate_qualipunkte(qualitipps):

    qualipunkte = {}

    for key in qualitipps:
        if key == 'Ergebnis':
            continue

        tuple1 = qualitipps[key]
        tuple2 = qualitipps['Ergebnis']

        # Gleiche Einträge an der gleichen Stelle
        same_position = [i for i in range(len(tuple1)) if tuple1[i] == tuple2[i]]

        # Gleiche Einträge, aber an unterschiedlichen Stellen
        different_position = [
            i for i in range(len(tuple1))
            if tuple1[i] in tuple2 and i != tuple2.index(tuple1[i])
        ]

        trefferpunkte = [25, 20, 15, 10]
        punkte_treffer = sum([trefferpunkte[i] for i in same_position])

        punkte_topvier = len(different_position) * 5

        punkte = punkte_treffer + punkte_topvier

        qualipunkte.update({key: punkte})

    return qualipunkte


def calculate_fastestLabPunkte(fastestlabtipps):
    fastestlabpunkte = {}

    for key in fastestlabtipps:
        if key == 'Ergebnis':
            continue

        tuple1 = fastestlabtipps[key]
        tuple2 = fastestlabtipps['Ergebnis']
        punkte = 0

        if tuple1 == tuple2:
            punkte = 15

        fastestlabpunkte.update({key: punkte})

    return fastestlabpunkte



def calculate_racepunkte(racetipps, wmStand):

    racepunkte = {}

    for key in racetipps:
        if key == 'Ergebnis':
            continue

        tuple1 = racetipps[key]
        tuple2 = racetipps['Ergebnis']

        # Gleiche Einträge an der gleichen Stelle
        same_position = [i for i in range(len(tuple1)) if tuple1[i] == tuple2[i]]

        # Einträge sind eine Position vorher
        position_before = [i for i in range(len(tuple1)-1) if tuple1[i] == tuple2[i+1]]

        # Einträge sind eine Position nachher
        position_after = [i+1 for i in range(len(tuple1) - 1) if tuple1[i+1] == tuple2[i]]

        # Gleiche Einträge, aber an unterschiedlichen Stellen
        #different_position = [
        #    i for i in range(len(tuple1))
        #    if tuple1[i] in tuple2 and i != tuple2.index(tuple1[i]) and i != tuple2.index(tuple1[i])-1 and i != tuple2.index(tuple1[i])+1
        #]
        different_position = []
        for i, val1 in enumerate(tuple1):
            if val1 in tuple2:
                # Index des Wertes im zweiten Tupel
                j = tuple2.index(val1)

                # Bedingung: Nicht gleiche Stelle oder Nachbarposition
                if abs(i - j) > 1:
                    different_position.append(val1)

        # Berechne Punkte
        trefferpunkte = 0

        for idx in same_position:
            if tuple1[idx] in wmStand:
                j = wmStand.index(tuple1[idx])
                trefferpunkte = trefferpunkte + abs(j-idx) * 10

        punkte_fastTreffer = (len(position_before) + len(position_after)) * 8
        punkte_topTen = len(different_position) * 4


        punkte = trefferpunkte + punkte_fastTreffer + punkte_topTen

        racepunkte.update({key: punkte})

    return racepunkte

