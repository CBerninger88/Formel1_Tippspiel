import requests

import utils
from db import get_db
from spieler import Spieler


class City:
    def __init__(self, city):
        """Konstruktor, der den Namen der Stadt inkl race_id speichert."""
        self.city = city.capitalize()
        self.race_id = 0#self.get_raceID()['race_id']
'''
    def get_raceID(self):
        db = get_db()
        cursor = db.cursor()
        # 2. race_id ermitteln
        cursor.execute('SELECT id FROM races WHERE city = %s', (self.city,))
        race_result = cursor.fetchone()
        if not race_result:
            return {'success': False, 'message': 'Race not found'}
        else:
            race_id = {'success': True, 'message': 'Race not found', 'race_id': race_result[0]}
            return race_id

    def get_wm_stand(self):

        db = get_db()
        cursor = db.cursor()

        # 3. Qualifying-Tipps aus der QualiTips-Tabelle auslesen
        cursor.execute("""
               SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10, driver11,
                        driver12, driver13, driver14, driver15, driver16, driver17, driver18, driver19, driver20
               FROM wmstand
               WHERE race_id = %s
               ORDER BY id DESC LIMIT 1
           """, (self.race_id,))
        wmStand = cursor.fetchone()

        # Falls ein WM-Stand gefunden wurde, diesen formatieren und zurückgeben
        if wmStand:
            return {f'wmdriver{i + 1}': driver for i, driver in enumerate(wmStand)}, {'success': True, 'message': 'Ok'}

        # Falls kein WM-Stand vorhanden ist, entsprechende Fehlermeldung zurückgeben
        message = 'Kein WM Stand beim ersten Rennen' if self.city == 'Melbourne' else 'WM Stand wurde noch nicht eingegeben'
        return {}, {'success': False, 'message': message}

    def set_wm_stand(self, wmdrivers):

        db = get_db()
        cursor = db.cursor()

        wmdrivers = wmdrivers[0:20]
'''
'''
        # 2. Daten in WMStand speichern
        cursor.execute(
                INSERT INTO wmstand (race_id, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, 
                                        driver9, driver10, driver11, driver12, driver13, driver14, driver15, driver16,
                                        driver17, driver18, driver19, driver20)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        , (self.race_id, *wmdrivers))
        db.commit()
'''
'''
    def get_lastyear_result(self):
        """Holt die Rennergebnisse des Vorjahres aus der API"""
        ergebnis = {}
        season = 2024
        round_number = self.get_round_number(self.city, 2024)

        if round_number is None:
            msg = f"Kein Rennen für {self.city} in {season} gefunden."
            return {}, {'success': False, 'message': msg}

        url = f"https://ergast.com/api/f1/{season}/{round_number}/results.json"
        response = requests.get(url)

        # Überprüfen, ob die Anfrage erfolgreich war
        if response.status_code != 200:
            return {}, {'success': False, 'message': 'Fehler beim Abrufen der API-Daten'}

        try:

            data = response.json()  # JSON-Daten extrahiere
            # Rennergebnisse aus den Daten extrahieren
            race_results = data["MRData"]["RaceTable"]["Races"][0]["Results"]

            # Ergebnisse anzeigen
            for pos, result in enumerate(race_results, start=1):
                driver_name = f"{result['Driver']['givenName'][0]}. {result['Driver']['familyName']}"
                ergebnis[f'lydriver{pos}'] = driver_name

            return ergebnis, {'success': True, 'message': 'Ok'}

        except (KeyError, IndexError):
            return {}, {'success': False, 'message': 'Datenstruktur nicht wie erwartet'}


    def get_lastyear_quali(self):
        """Holt die Startaufstellung des Vorjahres aus der API."""
        ergebnis = {}
        season = 2024
        round_number = self.get_round_number(self.city, 2024)

        if round_number is None:
            msg = f"Kein Rennen für {self.city} in {season} gefunden."
            return {}, {'success': False, 'message': msg}

        url = f"https://ergast.com/api/f1/{season}/{round_number}/results.json"
        response = requests.get(url)

        if response.status_code != 200:
            return {}, {'success': False, 'message': 'Fehler beim Abrufen der API-Daten'}

        data = response.json()  # JSON-Daten extrahieren

        try:
            # Rennergebnisse aus den Daten extrahieren
            qual_results = data["MRData"]["RaceTable"]["Races"][0]["Results"]

            # Ergebnisse anzeigen
            for result in qual_results:
                grid_position = int(result["grid"])  # Startplatz als Zahl
                if grid_position > 0:  # Fahrer, die aus der Box starten, haben grid = "0"
                    driver_name = f"{result['Driver']['givenName'][0]}. {result['Driver']['familyName']}"
                    ergebnis[f'lyqdriver{grid_position}'] = driver_name  # Fahrer nach Startposition speichern

            ergebnis = dict(sorted(ergebnis.items(), key=lambda x: int(x[0].split('driver')[-1])))
            return ergebnis, {'success': True, 'message': 'Ok'}

        except (KeyError, IndexError):
                return {}, {'success': False, 'message': 'Datenstruktur nicht wie erwartet'}


    def get_lastyear_fastestLab(self):
        """Holt die schnellste Rennrunde des Vorjahres aus der API."""
        season = 2024
        round_number = self.get_round_number(self.city, 2024)

        if round_number is None:
            msg = f"Kein Rennen für {self.city} in {season} gefunden."
            return {}, {'success': False, 'message': msg}

        url = f"https://ergast.com/api/f1/{season}/{round_number}/results.json"
        response = requests.get(url)

        if response.status_code != 200:
            return {}, {'success': False, 'message': 'Fehler beim Abrufen der API-Daten'}

        data = response.json()

        try:
            # Ergebnisse des Rennens abrufen
            race_results = data["MRData"]["RaceTable"]["Races"][0]["Results"]

            fastest_driver = None
            fastest_time = float('inf')

            fastest_lap_info = None
            for result in race_results:
                if "FastestLap" in result:
                    fastest_lap_info = result["FastestLap"]

                if fastest_lap_info:
                    lap_time_str = result["FastestLap"]["Time"]["time"]
                    lap_time = self.convert_time_to_seconds(lap_time_str)
                    driver_name = f"{result['Driver']['givenName'][0]}. {result['Driver']['familyName']}"

                    # Vergleiche die Zeiten, um den schnellsten Fahrer zu finden
                    if fastest_time is None or lap_time < fastest_time:
                        fastest_time = lap_time
                        fastest_driver = driver_name

                    fastest_lap_info = None

            if fastest_driver:
                return {f'lyfdriver': fastest_driver} , {'success': True, 'message': 'Ok'}
            else:
                return {}, {'success': False, 'message': 'Keine schnellste Runde in API gefunden'}

        except (KeyError, IndexError):
            return {}, {'success': False, 'message': 'Datenstruktur nicht wie erwartet'}



    def convert_time_to_seconds(self, time_str):
        """Konvertiert eine Zeit im Format 'M:SS.sss' oder 'SS.sss' in Sekunden als float."""
        test = 5
        try:
            if ":" in time_str:
                minutes, rest = time_str.split(":")
                seconds = float(rest)
                return int(minutes) * 60 + seconds  # Minuten in Sekunden umwandeln
            else:
                return float(time_str)  # Falls nur Sekunden vorhanden sind
        except ValueError:
            return float('inf')  # Falls ein Fehler auftritt, setzen wir eine unendlich große Zahl


    def get_round_number(self, city, season=2024):
        """Findet die Rundennummer (round_number) eines Rennens in einer bestimmten Stadt."""

        url = f"https://ergast.com/api/f1/{season}.json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            try:
                races = data["MRData"]["RaceTable"]["Races"]

                for race in races:
                    if city.lower() in race["Circuit"]["Location"]["locality"].lower():
                        return int(race["round"])  # Rundennummer zurückgeben

                return None  # Falls die Stadt nicht gefunden wurde

            except (KeyError, IndexError):
                return None  # Falls die API-Struktur unerwartet ist

        return None  # Falls die API nicht erreichbar ist

    def is_tipppunkte(self):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
                SELECT EXISTS (SELECT 1 FROM tipppunkte WHERE race_id = %s)
            """, (self.race_id,))
        exists = cursor.fetchone()[0]

        return exists

    def get_tipppunkte(self, calcnew):
        users = utils.get_users()
        tipppunkte = {}
        gesamtpunkte = {}
        success = True
        message = ''

        wmStand = self.get_wm_stand()
        if not wmStand:
            success = False
            message = f'Es gibt für {self.city} noch keinen WM Stand'
            return {}, {}, {'success': success, 'message': message}

        race_ergebnis, status = Spieler('Ergebnis').get_race_tipps(self.race_id)
        if not status['success']:
            success = False
            message = f'Es gibt für {self.city} noch kein Ergebnis'
            return {}, {}, {'success': success, 'message': message}

        no_tipps = []
        for name in users:
            if name == "Ergebnis":
                continue
            spieler = Spieler(name)
            if calcnew:
                qualipunkte, status1 = spieler.calculate_qualipunkte(self.race_id)
                tipppunkte.update({name: qualipunkte})
                if not status1['success']:
                    no_tipps.append(name)
                    continue
                racepunkte, status2 = spieler.calculate_racepunkte(wmStand, self.race_id)
                tipppunkte[name].update(racepunkte)
                fastestLabpunkte, status3 = spieler.calculate_fastestLab_tipps(self.race_id)
                tipppunkte[name].update(fastestLabpunkte)

                if not status2['success']:
                    success = False
                    message += status2['message']
                if not status3['success']:
                    success = False
                    message += status3['message']
            else:
                tipppunkte.update({name: spieler.get_tipppunkte(self.race_id)})
                if tipppunkte == {}:
                    success = False
                    message += 'Keine Daten aus der Datenbank erhalten.'

            gesamtpunkte.update({name: spieler.calculate_gesamtPunkte(tipppunkte[name])[0]})

        if no_tipps:
            success = True
            message = 'Folgende Spieler haben keine Tipps abgegeben: ' + ", ".join(no_tipps)
        else:
            message = 'Alles ok'

        status = {'success': success, 'message': message}
        return tipppunkte, gesamtpunkte, status

    def set_tipppunkte(self, tipppunkte):
        users = utils.get_users()
        for name in users:
            if name == "Ergebnis":
                continue
            spieler = Spieler(name)
            spieler.set_tipppunkte(self.race_id, tipppunkte[name])
'''