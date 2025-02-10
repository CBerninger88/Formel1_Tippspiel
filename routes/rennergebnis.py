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
    calcNew = data.get('calcNew')

    db = get_db()
    cursor = db.cursor()

    # 1. race_id ermitteln
    cursor.execute('SELECT id FROM races WHERE city = %s', (city,))
    race_result = cursor.fetchone()
    if not race_result:
        return jsonify({'success': False, 'message': 'Race not found'}), 400
    race_id = race_result[0]


    # 2. Existiert race_id in der tipppunkte Tabelle
    cursor.execute("""
        SELECT EXISTS (SELECT 1 FROM tipppunkte WHERE race_id = %s)
    """, (race_id,))
    exists = cursor.fetchone()[0]

    if exists and not calcNew:

        cursor.execute("""
            SELECT t.*, u.name
            FROM tipppunkte t
            JOIN users u ON t.user_id = u.id
            WHERE t.race_id = %s
            AND t.id IN (
                SELECT MAX(id) 
                FROM tipppunkte
                WHERE race_id = %s
                GROUP BY user_id
            )
            ORDER BY u.name;
        """, (race_id, race_id))

        # Alle letzten Einträge abrufen
        rows = cursor.fetchall()

        # Ausgabe der Ergebnisse
        result_dict = {}
        quali_keys = ['qpunkte1', 'qpunkte2', 'qpunkte3', 'qpunkte4']
        race_keys = ['rpunkte1', 'rpunkte2', 'rpunkte3', 'rpunkte4', 'rpunkte5', 'rpunkte6', 'rpunkte7', 'rpunkte8',
                     'rpunkte9', 'rpunkte10']

        if rows:
            for row in rows:
                name = row[-1]  # Name ist die letzte Spalte
                points = tuple(row[2:-2])  # Punkte sind die Spalten 2 bis vorletzte (qpunkte, rpunkte, fpunkte)
                result_dict[name] = {}
                for i, qkey in enumerate(quali_keys):
                    result_dict[name][qkey] = points[i]

                for i, rkey in enumerate(race_keys):
                    result_dict[name][rkey] = points[i+4]

                result_dict[name]['fpunkte'] = points[-1]

        else:
            print(f"Keine Daten für race_id {race_id} gefunden.")

        ergebnis = calculate_punkte(result_dict)

    else:
        ergebnis = insertPunkteinDB(race_id, city, db)





    return jsonify(ergebnis)



def insertPunkteinDB(race_id, city, db):

    cursor = db.cursor()


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
        return {'success': False, 'message': 'Es wurden noch keine Tipps für dieses Rennen abgegeben'}

    if 'Ergebnis' not in qualitipps:
        return {'success': False, 'message': 'Es wurden noch keine Ergebnis für dieses Rennen eingetragen'}

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
        return {'success': False, 'message': 'Es wurden noch keine Tipps für dieses Rennen abgegeben'}

    if 'Ergebnis' not in racetipps:
        return {'success': False, 'message': 'Es wurden noch keine Ergebnis für dieses Rennen eingetragen'}

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
        return {'success': False, 'message': 'Es wurden noch keine Tipps für die schnellste Runde abgegeben'}

    if 'Ergebnis' not in fastestlabtipps:
        return {'success': False, 'message': 'Es wurden noch keine Ergebnis für die schnellste Runde eingetragen'}

    # Den WM Stand holen
    if city != 'Melbourne':
        cursor.execute("""
                       SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10, driver11,
                                driver12, driver13, driver14, driver15, driver16, driver17, driver18, driver19, driver20
                       FROM wmstand
                       WHERE race_id = %s
                       ORDER BY id DESC LIMIT 1
                   """, (race_id,))
        wmStand = cursor.fetchone()
        if not wmStand:
            return {'success': False, 'message': 'Es gibt keinen WM Stand für dieses Rennen'}
    else:
        wmStand = None

    punkte = {}
    calculate_qualipunkte(qualitipps, punkte)
    message, success = calculate_racepunkte(racetipps, wmStand, punkte, city)
    calculate_fastestLabPunkte(fastestlabtipps, punkte)

    # 3. Daten in FastestLab speichern

    sql = """
            INSERT INTO tipppunkte (
                user_id, race_id, qpunkte1, qpunkte2, qpunkte3, qpunkte4,
                rpunkte1, rpunkte2, rpunkte3, rpunkte4, rpunkte5, rpunkte6,
                rpunkte7, rpunkte8, rpunkte9, rpunkte10, fpunkte
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    for name in punkte.keys():

        cursor.execute('SELECT id FROM users WHERE name = %s', (name,))
        user_result = cursor.fetchone()
        if not user_result:
            return {'success': False, 'message': 'User not found'}
        user_id = user_result[0]

        tipppunkte = punkte.get(name)
        values = (
            user_id,  # Hier könntest du eine tatsächliche ID anstelle des Namens verwenden
            race_id,
            tipppunkte.get('qpunkte1', 0), tipppunkte.get('qpunkte2', 0), tipppunkte.get('qpunkte3', 0),
            tipppunkte.get('qpunkte4', 0), tipppunkte.get('rpunkte1', 0), tipppunkte.get('rpunkte2', 0),
            tipppunkte.get('rpunkte3', 0), tipppunkte.get('rpunkte4', 0), tipppunkte.get('rpunkte5', 0),
            tipppunkte.get('rpunkte6', 0), tipppunkte.get('rpunkte7', 0), tipppunkte.get('rpunkte8', 0),
            tipppunkte.get('rpunkte9', 0), tipppunkte.get('rpunkte10', 0), tipppunkte.get('fpunkte', 0)
        )
        cursor.execute(sql, values)

    db.commit()

    ergebnis = calculate_punkte(punkte)
    ergebnis.update({'success': success, 'message': message})
    return ergebnis


def calculate_punkte(punkte):

    ergebnis = {}

    quali_keys = ['qpunkte1', 'qpunkte2', 'qpunkte3', 'qpunkte4']
    race_keys = ['rpunkte1', 'rpunkte2', 'rpunkte3', 'rpunkte4', 'rpunkte5', 'rpunkte6', 'rpunkte7', 'rpunkte8',
                  'rpunkte9', 'rpunkte10']
    for name in punkte.keys():

        ergebnis.update({name: {}})

        qPunkte = 0
        for qkey in quali_keys:
            qPunkte = qPunkte + punkte[name][qkey]
        ergebnis[name].update({'qPunkte': qPunkte})

        rPunkte = 0
        for rkey in race_keys:
            rPunkte = rPunkte + punkte[name][rkey]
        ergebnis[name].update({'rPunkte': rPunkte})

        fPunkte = punkte[name]['fpunkte']
        ergebnis[name].update({'fPunkte': fPunkte})

        gesamtPunkte = qPunkte + rPunkte + fPunkte
        ergebnis[name].update({'gesamtPunkte': gesamtPunkte})


    ergebnis.update({'success': True, 'message': 'Alles ok'})
    return ergebnis




def calculate_qualipunkte(qualitipps, punkte):

    qualipunkte = {}
    driver_key = ['qpunkte1', 'qpunkte2', 'qpunkte3', 'qpunkte4']
    trefferpunkte = [25, 20, 15, 10]

    for key in qualitipps:
        if key == 'Ergebnis':
            continue
        punkte.update({key: {}})
        tipps = qualitipps[key]
        ergebnis = qualitipps['Ergebnis']

        # Gleiche Einträge an der gleichen Stelle

        for i, tipp in enumerate(tipps):
            if tipp == ergebnis[i]:
                punkte[key].update({driver_key[i]: trefferpunkte[i] })
            elif tipp in ergebnis:
                punkte[key].update({driver_key[i]: 4})
            else:
                punkte[key].update({driver_key[i]: 0})



def calculate_fastestLabPunkte(fastestlabtipps, punkte):
    fastestlabpunkte = {}


    for name in fastestlabtipps:
        if name == 'Ergebnis':
            continue

        tipp = fastestlabtipps[name]
        ergebnis = fastestlabtipps['Ergebnis']


        if tipp == ergebnis:
            punkte[name].update({'fpunkte': 15})
        else:
            punkte[name].update({'fpunkte': 0})



def calculate_racepunkte(racetipps, wmStand, punkte, city):

    driver_key = ['rpunkte1', 'rpunkte2', 'rpunkte3', 'rpunkte4', 'rpunkte5', 'rpunkte6', 'rpunkte7', 'rpunkte8',
                  'rpunkte9', 'rpunkte10']

    for name in racetipps:
        if name == 'Ergebnis':
            continue

        tipps = racetipps[name]
        ergebnis = racetipps['Ergebnis']

        if name not in punkte:
            punkte.update({name: {}})

        # Gleiche Einträge an der gleichen Stelle

        for i, tipp in enumerate(tipps):
            if tipp == ergebnis[i]:

                if city == 'Melbourne':
                    punkte[name].update({driver_key[i]: 10})
                else:
                    if wmStand is not None and tipp in wmStand:
                        j = wmStand.index(tipp)
                        punkte[name].update({driver_key[i]: abs(j - i) * 10})
                    else:
                        punkte[name].update({driver_key[i]: 0})
                        message = 'Kein WM Stand vorhanden'
                        success = False

            elif tipp != ergebnis[i] and tipp in ergebnis:
                if wmStand is not None and tipp in wmStand:
                    j = wmStand.index(tipp)
                    if abs(i-j) > 1:
                        punkte[name].update({driver_key[i]: 4})
                    else:
                        punkte[name].update({driver_key[i]: 8})
                else:
                    if city == 'Melbourne':
                        punkte[name].update({driver_key[i]: 4})
                    else:
                        punkte[name].update({driver_key[i]: 0})
                        message = 'Kein WM Stand vorhanden'
                        success = False

            else:
                punkte[name].update({driver_key[i]: 0})
                message = f'Der Fahrer {tipp} von {name} ist nicht in der WM Liste'
                success = False

    return message, success