import utils
from city import City
from db import get_db
from spieler import Spieler


class Dummytipps(Spieler):
    def __init__(self, name):
        """Konstruktor, der den Namen des Spielers speichert."""
        super().__init__(name)


    def get_quali_tipps(self, race_id):
        ergebnis = {}
        status = {'success': False, 'message': 'Ok'}
        db = get_db()
        cursor = db.cursor()

        # 1. Versuch: Quali-Tipps aus der Datenbank abrufen
        cursor.execute("""
                   SELECT driver1, driver2, driver3, driver4
                   FROM qualitipps
                   WHERE user_id = %s AND race_id = %s
                   ORDER BY id DESC LIMIT 1
               """, (self.user_id, race_id))
        qresult = cursor.fetchone()

        if qresult is not None:
            ergebnis.update({f'qdriver{i + 1}': qresult[i] for i in range(len(qresult))})
            status['success'] = True
            return ergebnis, status

        # 2. Versuch: Alternativen basierend auf `self.name`
        if self.name in ["Dummy_LR", "Dummy_LY", "Dummy_WM"]:
            city_info = utils.get_cityName(race_id)
            if not city_info:
                status['message'] = 'Stadtname für Rennen nicht gefunden'
                return ergebnis, status

            city = City(city_info['cityName'])

            if self.name == "Dummy_LR":
                last_race = Spieler('Ergebnis')
                qdrivers = {}
                if race_id > 1:
                    qdrivers = last_race.get_quali_tipps(race_id - 1)[0]
                else:
                    status['message'] = 'Kein LR Tipp für erstes Rennen'

                if qdrivers != {}:
                    ergebnis.update(qdrivers)
                    self.set_quali_tipps(race_id, list(qdrivers.values()))
                    status['success'] = True
                else:
                    status['message'] = 'Es gibt noch kein Ergebnis aus vorherigem Rennen'

            elif self.name == "Dummy_LY":
                lyStand, lyStatus = city.get_lastyear_quali()
                if lyStatus['success']:
                    lyStand_list = [driver for driver in lyStand.values() if driver in utils.get_drivers()]
                    ergebnis = {f'qdriver{i + 1}': lyStand_list[i] for i in range(min(4, len(lyStand_list)))}
                    self.set_quali_tipps(race_id, lyStand_list[:4])
                    status = lyStatus

            elif self.name == "Dummy_WM":
                wmStand, wmStatus = city.get_wm_stand()
                if wmStatus['success']:
                    wmStand_list = [driver for driver in wmStand.values() if driver in utils.get_drivers()]
                    ergebnis = {f'qdriver{i + 1}': wmStand_list[i] for i in range(min(4, len(wmStand_list)))}
                    self.set_quali_tipps(race_id, wmStand_list[:4])
                    status = wmStatus
                else:
                    status = wmStatus

        return ergebnis, status

    def get_race_tipps(self, race_id):
        ergebnis = {}
        status = {'success': False, 'message': 'Ok'}
        db = get_db()
        cursor = db.cursor()

        # 1. Versuch: Renntipps aus der Datenbank abrufen
        cursor.execute("""
                            SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10
                            FROM racetipps
                            WHERE user_id = %s AND race_id = %s
                            ORDER BY id DESC LIMIT 1
                           """, (self.user_id, race_id))
        rresult = cursor.fetchone()

        if rresult is not None:
            ergebnis.update({f'rdriver{i + 1}': rresult[i] for i in range(len(rresult))})
            status['success'] = True
            return ergebnis, status

        # 2. Alternativer Ansatz basierend auf `self.name`
        if self.name in ["Dummy_LR", "Dummy_LY", "Dummy_WM"]:
            city_info = utils.get_cityName(race_id)
            if not city_info:
                status['message'] = 'Stadtname für Rennen nicht gefunden'
                return ergebnis, status

            city = City(city_info['cityName'])

            if self.name == "Dummy_LR":
                lastRace = Spieler('Ergebnis')
                rdrivers = {}
                if race_id > 1:
                    rdrivers = lastRace.get_race_tipps(race_id - 1)[0]
                else:
                    status['message'] = 'Kein LR Tipp für erstes Rennen'

                if rdrivers != {}:
                    ergebnis.update(rdrivers)
                    self.set_race_tipps(race_id, list(rdrivers.values()))
                    status['success'] = True
                else:
                    status['message'] = 'Es gibt noch kein Ergebnis aus vorherigem Rennen'

            elif self.name == "Dummy_LY":
                lyStand, lystatus = city.get_lastyear_result()

                if lystatus['success']:
                    lyStand_list = [driver for driver in lyStand.values() if driver in utils.get_drivers()]
                    ergebnis = {f'rdriver{i + 1}': lyStand_list[i] for i in range(min(10, len(lyStand_list)))}
                    self.set_race_tipps(race_id, lyStand_list[:10])
                    status = lystatus
                else:
                    status = lystatus

            elif self.name == "Dummy_WM":
                wmStand, wmstatus = city.get_wm_stand()

                if wmstatus['success']:
                    wmStand_list = [driver for driver in wmStand.values() if driver in utils.get_drivers()]
                    ergebnis = {f'rdriver{i + 1}': wmStand_list[i] for i in range(min(10, len(wmStand_list)))}
                    self.set_race_tipps(race_id, wmStand_list[:10])
                    status = wmstatus
                else:
                    status = wmstatus


        return ergebnis, status

    def get_fastestlab_tipp(self, race_id):
        ergebnis = {}
        status = {'success': False, 'message': 'Ok'}
        db = get_db()
        cursor = db.cursor()

        # 1. Versuch: Renntipps aus der Datenbank abrufen
        cursor.execute("""
                    SELECT driver1
                    FROM fastestlab
                    WHERE user_id = %s AND race_id = %s
                    ORDER BY id DESC LIMIT 1
                    """, (self.user_id, race_id))
        fresult = cursor.fetchone()

        if fresult is not None:
            ergebnis.update({f'fdriver': fresult[0]})
            status['success'] = True
            return ergebnis, status


        # Falls kein Tipp in der DB gefunden wurde → Fallback-Logik
        if self.name in ['Dummy_LR', 'Dummy_WM']:
            if race_id > 1:
                lastRace = Spieler('Ergebnis')
                fdrivers = lastRace.get_fastestlab_tipp(race_id - 1)[0]

                if fdrivers != {}:
                    ergebnis['fdriver'] = list(fdrivers.values())[0]
                    self.set_fastestLab_tipps(race_id, ergebnis['fdriver'])  # Speichern
                    status['success'] = True
                else:
                    status['message'] = 'Es gibt noch kein Ergebnis aus vorherigem Rennen'

            else:
                status['message'] = 'Kein LR Tipp für erstes Rennen'

        elif self.name == "Dummy_LY":
                cityName = utils.get_cityName(race_id)
                if cityName:
                    city = City(cityName['cityName'])
                    fdriver, status = city.get_lastyear_fastestLab()

                    # Prüfen, ob Fahrer noch aktiv ist
                    drivers = set(utils.get_drivers())
                    fdriver_list = [d for d in fdriver.values() if d in drivers]


                    if status['success']:
                        ergebnis['fdriver'] = fdriver_list[0]
                        self.set_fastestLab_tipps(race_id, ergebnis['fdriver'])
                    else:
                        status['message'] = 'Kein passender Fahrer für Fallback gefunden'

        return ergebnis, status


    def set_quali_tipps(self, race_id, qdrivers, tipprunde_id):

        test = 4
        return test