import requests

from db import get_db


class City:
    def __init__(self, city):
        """Konstruktor, der den Namen des Spielers speichert."""
        self.city = city.capitalize()
        self.race_id = self.get_raceID()['race_id']

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

        ergebnis = {}
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

        if wmStand:
            # Dynamisch Fahrer in ein Dictionary packen
            ergebnis = {f'wmdriver{i + 1}': wmStand[i] for i in range(len(wmStand))}

        else:

            if self.city == 'Melbourne':
                return {}, {'success': False, 'message': 'Kein WM Stand beim ersten Rennen'}

            season = 2024
            round_number = self.race_id - 1

            url = f"https://ergast.com/api/f1/{season}/{round_number}/driverStandings.json"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                i = 0
                for driver_info in data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
                    driver_name = f"{driver_info['Driver']['givenName'][0]}. {driver_info['Driver']['familyName']}"
                    # points = driver_info['points']
                    # team = driver_info['Constructors'][0]['name']
                    ergebnis.update({f'wmdriver{i + 1}': driver_name})
                    i = i + 1

                self.set_wm_stand(list(ergebnis.values()))
                #ergebnis.update({'success': True})

            else:
                return {}, {'success': False, 'message': 'Keine Daten von API erhalten'}

        return ergebnis, {'success': True}

    def set_wm_stand(self, wmdrivers):

        db = get_db()
        cursor = db.cursor()

        wmdrivers = wmdrivers[0:20]

        # 2. Daten in WMStand speichern
        cursor.execute('''
                INSERT INTO wmstand (race_id, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, 
                                        driver9, driver10, driver11, driver12, driver13, driver14, driver15, driver16,
                                        driver17, driver18, driver19, driver20)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (self.race_id, *wmdrivers))
        db.commit()

    def get_lastyear_result(self):
        ergebnis = {}
        season = 2024
        round_number = self.race_id

        url = f"https://ergast.com/api/f1/{season}/{round_number}/driverStandings.json"

        response = requests.get(url)

        # Überprüfen, ob die Anfrage erfolgreich war
        if response.status_code == 200:
            data = response.json()  # JSON-Daten extrahieren

            # Rennergebnisse aus den Daten extrahieren
            driver_standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
            i = 0

            # Ergebnisse anzeigen
            for driver_info in driver_standings:
                #position = result['position']
                driver_name = f"{driver_info['Driver']['givenName'][0]}. {driver_info['Driver']['familyName']}"
                #constructor = result['Constructor']['name']
                ergebnis.update({f'lydriver{i + 1}': driver_name})
                i = i + 1


        return ergebnis, {'success': True}