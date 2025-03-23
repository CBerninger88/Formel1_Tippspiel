import utils
from city import City
from db import get_db
from spieler import Spieler


class Dummy(Spieler):
    def __init__(self, name):
        """Konstruktor, der den Namen des Spielers speichert."""
        super().__init__(name)


    def get_quali_tipps(self, race_id):
        ergebnis = {}
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
                   SELECT driver1, driver2, driver3, driver4
                   FROM qualitipps
                   WHERE user_id = %s AND race_id = %s
                   ORDER BY id DESC LIMIT 1
               """, (self.user_id, race_id))
        qresult = cursor.fetchone()
        if qresult is not None:
            ergebnis.update({f'qdriver{i + 1}': qresult[i] for i in range(len(qresult))})
        else:
            if self.name == "Dummy_LR":
                lastRace = Spieler('Ergebnis')
                qdrivers = {}
                if race_id > 1:
                    qdrivers = lastRace.get_quali_tipps(race_id - 1)

                if qdrivers != {}:
                    ergebnis.update(qdrivers)
                    self.set_quali_tipps(race_id, list(qdrivers.values()))
            elif self.name == "Dummy_LY":
                cityName = utils.get_cityName(race_id)
                city = City(cityName['cityName'])
                lyStand, success = city.get_lastyear_quali()
                lyStand_list = list(lyStand.values())
                drivers = list(utils.get_drivers())
                lyStand_list = [element for element in lyStand_list if element in drivers]

                if success['success']:
                    ergebnis.update({f'qdriver{i + 1}': lyStand_list[i] for i in range(4)})
                    self.set_quali_tipps(race_id, lyStand_list[0:4])

            elif self.name == "Dummy_WM":
                cityName = utils.get_cityName(race_id)
                city = City(cityName['cityName'])
                wmStand, success = city.get_wm_stand()
                wmStand_list = list(wmStand.values())
                drivers = list(utils.get_drivers())
                wmStand_list = [element for element in wmStand_list if element in drivers]

                if success['success']:
                    ergebnis.update({f'qdriver{i + 1}': wmStand_list[i] for i in range(4)})
                    self.set_quali_tipps(race_id, wmStand_list[0:4])

        return ergebnis

    def get_race_tipps(self, race_id):
        ergebnis = {}
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
                            SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10
                            FROM racetipps
                            WHERE user_id = %s AND race_id = %s
                            ORDER BY id DESC LIMIT 1
                           """, (self.user_id, race_id))
        rresult = cursor.fetchone()
        if rresult is not None:
            ergebnis.update({f'rdriver{i + 1}': rresult[i] for i in range(len(rresult))})
        else:
            if self.name == "Dummy_LR":
                lastRace = Spieler('Ergebnis')
                rdrivers = {}
                if race_id > 1:
                    rdrivers = lastRace.get_race_tipps(race_id - 1)

                if rdrivers != {}:
                    ergebnis.update(rdrivers)
                    self.set_race_tipps(race_id, list(rdrivers.values()))
            elif self.name == "Dummy_LY":
                cityName = utils.get_cityName(race_id)
                city = City(cityName['cityName'])
                lyStand, success = city.get_lastyear_result()
                lyStand_list = list(lyStand.values())
                drivers = list(utils.get_drivers())
                lyStand_list = [element for element in lyStand_list if element in drivers]

                if success['success']:
                    ergebnis.update({f'rdriver{i + 1}': lyStand_list[i] for i in range(10)})
                    self.set_race_tipps(race_id, lyStand_list[0:10])

            elif self.name == "Dummy_WM":
                cityName = utils.get_cityName(race_id)
                city = City(cityName['cityName'])
                wmStand, success = city.get_wm_stand()
                wmStand_list = list(wmStand.values())
                drivers = list(utils.get_drivers())
                wmStand_list = [element for element in wmStand_list if element in drivers]

                if success['success']:
                    ergebnis.update({f'rdriver{i + 1}': wmStand_list[i] for i in range(10)})
                    self.set_race_tipps(race_id, wmStand_list[0:10])

        return ergebnis

    def get_fastestlab_tipp(self, race_id):
        ergebnis = {}
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
                    SELECT driver1
                    FROM fastestlab
                    WHERE user_id = %s AND race_id = %s
                    ORDER BY id DESC LIMIT 1
                    """, (self.user_id, race_id))
        fresult = cursor.fetchone()

        if fresult is not None:
            ergebnis.update({f'fdriver': fresult[0]})

        else:
            if self.name == "Dummy_LR" or self.name == "Dummy_WM":
                lastRace = Spieler('Ergebnis')
                fdrivers = {}
                if race_id > 1:
                    fdrivers = lastRace.get_fastestlab_tipp(race_id - 1)

                if fdrivers != {}:
                    ergebnis.update(fdrivers)
                    self.set_fastestLab_tipps(race_id, list(fdrivers.values()))

            elif self.name == "Dummy_LY":
                cityName = utils.get_cityName(race_id)
                city = City(cityName['cityName'])
                fdriver, success = city.get_lastyear_fastestLab()
                fdriver_list = list(fdriver.values())
                drivers = list(utils.get_drivers())
                fdriver_list = [element for element in fdriver_list if element in drivers]

                if success['success']:
                    ergebnis.update({f'fdriver': fdriver_list[0]})
                    self.set_fastestLab_tipps(race_id, fdriver_list[0])

        return ergebnis