import psycopg2
from psycopg2.extras import RealDictCursor
from db import get_db
from flask import jsonify
from collections import defaultdict

from models.dummy import Dummytipps
from spieler import Spieler


def get_cities(saison):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT re.city, r.id, r.date, r.is_sprint
        FROM races r
        JOIN race_events re ON r.race_event_id = re.id
        WHERE r.saison = %s
        ORDER BY r.date ASC;
    """, (saison,))
    result = cursor.fetchall()

    # Liste der Städte extrahieren
    cities = {
        name: {
            "race_id": race_id,
            "datum": datum,
            "is_sprint": is_sprint
        }
        for name, race_id, datum, is_sprint in result
    }
    return cities

def get_sprintCities(saison):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT re.city, r.id, r.date, r.is_sprint
        FROM races r
        JOIN race_events re ON r.race_event_id = re.id
        WHERE r.is_sprint = TRUE
          AND EXTRACT(YEAR FROM r.date)::int = %s
        ORDER BY r.date ASC;
    """, (saison,))

    result = cursor.fetchall()

    # Liste der Städte extrahieren
    cities = {
        name: {
            "race_id": race_id,
            "datum": datum,
            "is_sprint": is_sprint
        }
        for name, race_id, datum, is_sprint in result
    }
    return cities


def get_drivers():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM drivers ORDER BY name ASC;")
    result = cursor.fetchall()

    # Liste der Fahrer extrahieren
    drivers = [row[0] for row in result]
    return drivers

def get_users_in_tipprunde(tipprunde_id):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # 🔹 User der aktiven Tipprunde
    cursor.execute("""
           SELECT u.id, u.username
           FROM users u
           JOIN tipprunden_user tu ON tu.user_id = u.id
           WHERE tu.tipprunde_id = %s
           ORDER BY u.username
       """, (tipprunde_id,))
    users = cursor.fetchall()

    users = sorted(
        users,
        key=lambda u: (
            2 if u["username"] == "Ergebnis"
            else 1 if u["username"].startswith("Dummy_")
            else 0,
            u["username"].lower()
        )
    )

    return users


def get_user_id(name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (name,))
    result = cursor.fetchone()

    if not result:
        return {'success': False, 'message': 'User not found'}
    else:
        race_id = {'success': True, 'message': 'User found', 'user_id': result[0]}
        return race_id


def get_raceID(city, saison):
    db = get_db()
    cursor = db.cursor()
    # 2. race_id ermitteln
    cursor.execute("""
            SELECT r.id
            FROM races r
            JOIN race_events re ON r.race_event_id = re.id
            WHERE re.city = %s AND EXTRACT(YEAR FROM r.date)::int = %s
            LIMIT 1;
        """, (city, saison))
    race_result = cursor.fetchone()
    if not race_result:
        return {'success': False, 'message': 'Race not found'}
    else:
        race_id = {'success': True, 'message': 'Race not found', 'race_id': race_result[0]}
        return race_id


def get_min_raceID(saison):
    db = get_db()
    cursor = db.cursor()
    # 2. race_id ermitteln
    cursor.execute('SELECT MIN(id) FROM races WHERE EXTRACT(YEAR FROM date) = %s', (saison,))
    race_result = cursor.fetchone()
    if not race_result:
        return {'success': False, 'message': 'Kein Rennen in dieser Saison'}
    else:
        race_id = {'success': True, 'message': 'Min Race ID gefunden', 'race_id': race_result[0]}
        return race_id

def get_cityName(race_id):
    db = get_db()
    cursor = db.cursor()
    # 2. race_id ermitteln
    cursor.execute("""
        SELECT revent.city
        FROM races r
        JOIN race_events revent ON r.race_event_id = revent.id
        WHERE r.id = %s
    """, (race_id,))
    race_result = cursor.fetchone()
    if not race_result:
        return {'success': False, 'message': 'Race not found'}
    else:
        race_id = {'success': True, 'message': 'Race not found', 'cityName': race_result[0]}
        return race_id

def is_sprint(race_id):
    db = get_db()
    cursor = db.cursor()
    # 2. race_id ermitteln
    cursor.execute("""
        SELECT is_sprint
        FROM races
        WHERE id = %s;
    """, (race_id,))

    result = cursor.fetchone()
    if not result:
        return {'success': False, 'message': 'Race not found'}
    else:
        is_sprint = result[0]
        return is_sprint


def get_tipper(race_id, tipprunde_id, table_name):
    db = get_db()
    cursor = db.cursor()
    query = f"""
        SELECT DISTINCT u.username
        FROM {table_name} t
        JOIN users u ON t.user_id = u.id
        WHERE t.race_id = %s AND t.tipprunde_id = %s
        ORDER BY u.username
    """
    cursor.execute(query, (race_id, tipprunde_id))
    result = cursor.fetchall()
    names = [row[0] for row in result]
    return names

def get_qualiergebnis(race_id, saison):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = """
        SELECT driver1, driver2, driver3, driver4
        FROM qualiergebnisse
        WHERE race_id = %s AND saison = %s
        ORDER BY created_at DESC
        LIMIT 1;
    """

    cursor.execute(query, (race_id, saison))
    result = cursor.fetchall()

    if result:
        # Prefix von driverX → qdriverX
        return {f"q{key}": value for key, value in dict(result[0]).items()}, {'success': True, 'message': 'Ok'}

    message = 'Es gibt noch kein Quali-Ergebnis'
    return {}, {'success': False, 'message': message}




def get_rennergebnis(race_id, saison):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = f"""
        SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10, driver11,
                        driver12, driver13, driver14, driver15, driver16, driver17, driver18, driver19, driver20
        FROM rennergebnisse
        WHERE race_id = %s
        AND saison = %s
        ORDER BY created_at DESC
        LIMIT 1;
    """
    cursor.execute(query, (race_id, saison))
    result = cursor.fetchall()

    if result:
        return {f"r{key}": value for key, value in dict(result[0]).items()}, {'success': True, 'message': 'Ok'}

    # Falls kein WM-Stand vorhanden ist, entsprechende Fehlermeldung zurückgeben
    message = 'Es gibt noch kein Rennergebnis'
    return {}, {'success': False, 'message': message}

def get_sprintergebnis(race_id, saison):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = f"""
        SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8
        FROM sprintergebnisse
        WHERE race_id = %s
        AND saison = %s
        ORDER BY created_at DESC
        LIMIT 1;
    """
    cursor.execute(query, (race_id, saison))
    result = cursor.fetchall()

    if result:
        return dict(result[0]), {'success': True, 'message': 'Ok'}

    # Falls kein WM-Stand vorhanden ist, entsprechende Fehlermeldung zurückgeben
    message = 'Es gibt noch kein Rennergebnis'
    return {}, {'success': False, 'message': message}


def get_fastestlap_ergebnis(race_id, saison):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = """
        SELECT driver1
        FROM fastestlapergebnisse
        WHERE race_id = %s AND saison = %s
        ORDER BY created_at DESC
        LIMIT 1;
    """

    cursor.execute(query, (race_id, saison))
    result = cursor.fetchall()

    if result:
        return {f"f{key}": value for key, value in dict(result[0]).items()}, {'success': True, 'message': 'Ok'}

    message = 'Es gibt noch kein Ergebnis für die schnellste Runde'
    return {}, {'success': False, 'message': message}

def set_qualiergebnis(race_id, saison, drivers):
    """
    drivers = [driver1, driver2, driver3, driver4]
    """
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO qualiergebnisse (race_id, saison, driver1, driver2, driver3, driver4)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (race_id, saison, *drivers))

    db.commit()



def set_rennergebnis(race_id, saison, drivers):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        INSERT INTO rennergebnisse (race_id, saison, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10, driver11, driver12, driver13, driver14, driver15, driver16, driver17, driver18, driver19, driver20)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (race_id, saison, *drivers,))
    db.commit()


def set_fastestlap_ergebnis(race_id, saison, driver):
    """
    driver = 'Hamilton'
    """
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO fastestlapergebnisse (race_id, saison, driver1)
        VALUES (%s, %s, %s)
    """, (race_id, saison, *driver))

    db.commit()



def set_sprintergebnis(race_id, saison, drivers):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        INSERT INTO sprintergebnisse (race_id, saison, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (race_id, saison, *drivers,))
    db.commit()


def get_wm_stand(race_id, saison):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
        SELECT DISTINCT ON (race_id) driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10, driver11,
                        driver12, driver13, driver14, driver15, driver16, driver17, driver18, driver19, driver20
        FROM rennergebnisse
        WHERE saison = %s
        AND race_id <= %s
        ORDER BY race_id, created_at DESC;
    """, (saison, race_id))

    rennergebnisse = cursor.fetchall()

    cursor.execute("""
            SELECT DISTINCT ON (race_id) driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8
            FROM sprintergebnisse
            WHERE saison = %s
            AND race_id <= %s
            ORDER BY race_id, created_at DESC;
        """, (saison, race_id))

    sprintergebnisse = cursor.fetchall()


    fahrer_stats = berechne_wm_stand(rennergebnisse, sprintergebnisse)

    rangliste = sorted(
        fahrer_stats.items(),
        key=sort_key
    )

    wm_stand = []

    for i, (driver, stats) in enumerate(rangliste):
        wm_stand.append({
            "platz": i + 1,
            "driver": driver,
            "punkte": stats["punkte"]
        })

    return wm_stand, {'success': True, 'message': 'Ok'}



def berechne_wm_stand(rennergebnisse, sprintergebnisse):

    RACE_PUNKTE = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    SPRINT_PUNKTE = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}

    fahrer_stats = defaultdict(lambda: {
        "punkte": 0,
        "platzierungen": [0] * 20  # Index 0 = Platz 1
    })

    for rennen in rennergebnisse:
        for platz in range(1, 21):
            driver = rennen[f'driver{platz}']
            if not driver:
                continue

            fahrer_stats[driver]["punkte"] += RACE_PUNKTE.get(platz, 0)
            fahrer_stats[driver]["platzierungen"][platz - 1] += 1

    for sprint in sprintergebnisse:
        for platz in range(1, 9):
            driver = sprint[f'driver{platz}']
            if not driver:
                continue

            fahrer_stats[driver]["punkte"] += SPRINT_PUNKTE.get(platz, 0)

    return fahrer_stats

def sort_key(item):
    stats = item[1]
    return (
        -stats["punkte"],
        *(-p for p in stats["platzierungen"])
    )

def get_team_stand(race_id, saison):
    fahrer_wm, _ = get_wm_stand(race_id, saison)
    return berechne_team_wm_stand(fahrer_wm)


def berechne_team_wm_stand(fahrer_wm):
    driver_to_team = get_driver_team_mapping()

    team_punkte = defaultdict(int)

    for row in fahrer_wm:
        driver = row["driver"]
        punkte = row["punkte"]

        team = driver_to_team.get(driver)
        if not team:
            continue

        team_punkte[team] += punkte

    team_wm = [
        {"team": team, "punkte": punkte}
        for team, punkte in team_punkte.items()
    ]

    team_wm.sort(key=lambda x: -x["punkte"])

    for i, team in enumerate(team_wm):
        team["platz"] = i + 1

    return team_wm

def get_driver_team_mapping():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT name, team
        FROM drivers
    """)
    return dict(cursor.fetchall())

def set_dummies(race_id, saison, qdrivers, rdrivers, fdriver):

    dummy_service = Dummytipps()

    # Nur falls noch nicht letztes race der Saison
    min_race_id = get_min_raceID(saison)
    races = get_cities(saison)
    if race_id - (min_race_id['race_id'] - 1) < len(races):
        race_id_new = race_id + 1
    else:
        return

    sprint = is_sprint(race_id+1)


    ####### Dummy_LR #####
    dummy_id = get_user_id('Dummy_LR')['user_id']

    dummy_service.save_tipps(dummy_id, race_id_new, saison, qdrivers, 'quali')
    dummy_service.save_tipps(dummy_id, race_id_new, saison, rdrivers[0:10], 'race')
    dummy_service.save_tipps(dummy_id, race_id_new, saison, fdriver, 'fastest')

    if sprint:
        dummy_service.save_tipps(dummy_id, race_id_new, saison, rdrivers[0:8], 'sprint')


    ##### Dummy_WM #####
    dummy_id = get_user_id('Dummy_WM')['user_id']
    wm_stand, _ = get_wm_stand(race_id, saison)
    top4_drivers = [entry["driver"] for entry in wm_stand if 1 <= entry["platz"] <= 4]
    top10_drivers = [entry["driver"] for entry in wm_stand if 1 <= entry["platz"] <= 10]

    dummy_service.save_tipps(dummy_id, race_id_new, saison, top4_drivers, 'quali')
    dummy_service.save_tipps(dummy_id, race_id_new, saison, top10_drivers, 'race')
    dummy_service.save_tipps(dummy_id, race_id_new, saison, fdriver, 'fastest')

    if sprint:
        dummy_service.save_tipps(dummy_id, race_id_new, saison, top10_drivers[0:8], 'sprint')

    ##### Dummy_Kon #####
    dummy_id = get_user_id('Dummy_Kon')['user_id']
    team_wm = get_team_stand(race_id, saison)
    driver_team_mapping = get_driver_team_mapping()
    top5_teams = [team["team"] for team in team_wm[:5]]

    team_to_drivers = defaultdict(list)

    for row in wm_stand:
        driver = row["driver"]
        team = driver_team_mapping.get(driver)

        if team in top5_teams:
            team_to_drivers[team].append(row)

    for team in team_to_drivers:
        team_to_drivers[team].sort(key=lambda x: x["platz"])

    top10_team_drivers = []
    for team in top5_teams:
        top10_team_drivers.extend(team_to_drivers.get(team, []))

    top4_team_drivers = [entry["driver"] for entry in top10_team_drivers if 1 <= entry["platz"] <= 4]
    top10_team_drivers = [entry["driver"] for entry in top10_team_drivers]

    dummy_service.save_tipps(dummy_id, race_id_new, saison, top4_team_drivers, 'quali')
    dummy_service.save_tipps(dummy_id, race_id_new, saison, top10_team_drivers, 'race')
    dummy_service.save_tipps(dummy_id, race_id_new, saison, fdriver, 'fastest')

    if sprint:
        dummy_service.save_tipps(dummy_id, race_id_new, saison, top10_team_drivers[0:8], 'sprint')


    ##### Dummy_LY #####
    dummy_id = get_user_id('Dummy_LY')['user_id']
    saison_ly = saison - 1
    city_name = get_cityName(race_id_new)
    race_id_ly = get_raceID(city_name['cityName'], saison_ly)

    if race_id_ly['success']:
        race_id_ly = race_id_ly['race_id']
        qualiergebnis_ly, status = get_qualiergebnis(race_id_ly, saison_ly)
        rennergebnis_ly, status = get_rennergebnis(race_id_ly, saison_ly)
        fastest_driver_ly, status = get_fastestlap_ergebnis(race_id_ly, saison_ly)

        qualiergebnis_ly_list = list(qualiergebnis_ly.values())
        rennergebnis_ly_list = list(rennergebnis_ly.values())
        fastest_driver_ly_list = list(fastest_driver_ly.values())

        dummy_service.save_tipps(dummy_id, race_id_new, saison, qualiergebnis_ly_list, 'quali')
        dummy_service.save_tipps(dummy_id, race_id_new, saison, rennergebnis_ly_list[0:10], 'race')
        dummy_service.save_tipps(dummy_id, race_id_new, saison, fastest_driver_ly_list, 'fastest')

        if sprint:
            sprintergebnis_ly, status = get_sprintergebnis(race_id_ly, saison_ly)
            sprintergebnis_ly_list = list(sprintergebnis_ly.values())
            dummy_service.save_tipps(dummy_id, race_id_new, saison, sprintergebnis_ly_list, 'sprint')

    else:
        dummy_service.save_tipps(dummy_id, race_id_new, saison, top4_drivers, 'quali')
        dummy_service.save_tipps(dummy_id, race_id_new, saison, top10_drivers, 'race')
        dummy_service.save_tipps(dummy_id, race_id_new, saison, fdriver, 'fastest')

        if sprint:
            dummy_service.save_tipps(dummy_id, race_id_new, saison, top10_drivers[0:8], 'sprint')


def set_zusatztipp(zusatz_data: dict):
    """
    Fügt einen Eintrag in die Tabelle 'zusatztipps' ein.

    :param zusatz_data: Dictionary mit Keys = Spaltennamen in 'zusatztipps'.
                        z.B. {'wmdriver1': 'C. Leclerc', 'sdwm': 1, 'tipprunde_id': 15, ...}
    """
    db = get_db()
    cursor = db.cursor()

    # Konvertiere leere Strings für INT-Spalten zu None
    for key in ['sdwm', 'anzahlsieger']:
        if key in zusatz_data and zusatz_data[key] == '':
            zusatz_data[key] = None
        elif key in zusatz_data and zusatz_data[key] is not None:
            zusatz_data[key] = int(zusatz_data[key])

    # Spalten und Platzhalter für SQL vorbereiten
    columns = list(zusatz_data.keys())  # z.B. ['wmdriver1', 'wmdriver2', ..., 'tipprunde_id', 'user_id', 'saison']
    placeholders = ', '.join(['%s'] * len(columns))
    sql = f"INSERT INTO zusatztipps ({', '.join(columns)}) VALUES ({placeholders})"

    # Werte als Tuple
    values = [zusatz_data[col] for col in columns]

    # Ausführen und commit
    cursor.execute(sql, values)
    db.commit()


def get_zusatztipps(user_id, tipprunde_id, saison):
    """
    Liefert die aktuellsten Zusatztipps eines Users für eine bestimmte Tipprunde und Saison
    als Dictionary mit Spaltennamen als Keys.
    """
    db = get_db()
    cursor = db.cursor()

    # Alle Spalten außer id auswählen
    columns = [
        'wmdriver1', 'wmdriver2', 'wmdriver3',
        'pptrophydriver', 'flawarddriver',
        'sdwm', 'anzahlsieger',
        'team1', 'team2', 'team3', 'team4', 'team5',
        'team6', 'team7', 'team8', 'team9', 'team10', 'team11'
    ]

    sql = f"""
        SELECT {', '.join(columns)}
        FROM zusatztipps
        WHERE user_id = %s
          AND tipprunde_id = %s
          AND saison = %s
        ORDER BY id DESC
        LIMIT 1
    """

    cursor.execute(sql, (user_id, tipprunde_id, saison))
    row = cursor.fetchone()

    if row:
        # Als Dictionary zurückgeben
        return dict(zip(columns, row))
    else:
        return None  # kein Tipp gefunden

