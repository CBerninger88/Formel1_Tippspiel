import utils
from db import get_db

class Spieler:
    def __init__(self, name):
        """Konstruktor, der den Namen des Spielers speichert."""
        self.name = name
        self.user_id = self.get_user_id()

    def get_user_id(self):
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id FROM users WHERE name = %s', (self.name,))
        user_result = cursor.fetchone()
        user_id = user_result[0]
        return user_id

    def get_tipppunkte(self, race_id):
        ergebnis = {}
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
                            SELECT t.* 
                            FROM tipppunkte t
                            WHERE t.user_id = %s AND t.race_id = %s
                            ORDER BY t.id DESC
                            LIMIT 1;
                        """, (self.user_id, race_id))
        tipppunkte = cursor.fetchone()
        if tipppunkte is not None:
            tipppunkte = tipppunkte[2:]
            ergebnis.update({f'qpunkte{i + 1}': tipppunkte[i] for i in range(4)})
            ergebnis.update({f'rpunkte{i - 3}': tipppunkte[i] for i in range(4,14)})
            ergebnis.update({f'fpunkte': tipppunkte[i] for i in range(14, 15)})
        return ergebnis

    def set_tipppunkte(self, race_id, tipppunkte):

        db = get_db()
        cursor = db.cursor()
        sql = """
                    INSERT INTO tipppunkte (
                        user_id, race_id, qpunkte1, qpunkte2, qpunkte3, qpunkte4,
                        rpunkte1, rpunkte2, rpunkte3, rpunkte4, rpunkte5, rpunkte6,
                        rpunkte7, rpunkte8, rpunkte9, rpunkte10, fpunkte
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

        values = (
                self.user_id,  # Hier könntest du eine tatsächliche ID anstelle des Namens verwenden
                race_id,
                tipppunkte.get('qpunkte1', 0), tipppunkte.get('qpunkte2', 0), tipppunkte.get('qpunkte3', 0),
                tipppunkte.get('qpunkte4', 0), tipppunkte.get('rpunkte1', 0), tipppunkte.get('rpunkte2', 0),
                tipppunkte.get('rpunkte3', 0), tipppunkte.get('rpunkte4', 0), tipppunkte.get('rpunkte5', 0),
                tipppunkte.get('rpunkte6', 0), tipppunkte.get('rpunkte7', 0), tipppunkte.get('rpunkte8', 0),
                tipppunkte.get('rpunkte9', 0), tipppunkte.get('rpunkte10', 0), tipppunkte.get('fpunkte', 0)
            )
        cursor.execute(sql, values)
        db.commit()

    def calculate_qualipunkte(self, race_id):

        trefferpunkte = [25, 20, 15, 10]
        qpunkte = {}

        qualitipps, status1 = self.get_quali_tipps(race_id)
        qualitipps = list(qualitipps.values())
        quali_ergebnis, status2 = Spieler('Ergebnis').get_quali_tipps(race_id)
        quali_ergebnis = list(quali_ergebnis.values())

        if status1['success'] and status2['success']:
            for i, tipp in enumerate(qualitipps):
                if tipp == quali_ergebnis[i]:
                    qpunkte.update({f'qpunkte{i + 1}': trefferpunkte[i]})
                elif tipp in quali_ergebnis:
                    qpunkte.update({f'qpunkte{i + 1}': 4})
                else:
                    qpunkte.update({f'qpunkte{i + 1}': 0})
            msg = 'Alles ok'
            success = True
            return qpunkte, {'success': success, 'message': msg}

        if not status2['success']:
            msg = f'Es ist noch kein Ergebnis eingetragen. '
            success = False
            return qpunkte, {'success': success, 'message': msg}
        if not status1['success']:
            msg = status1['message']
            success = False
            return qpunkte, {'success': success, 'message': msg}


    def calculate_racepunkte(self, wmStand, race_id):

        rpunkte = {}

        racetipps, status1 = self.get_race_tipps(race_id)
        racetipps = list(racetipps.values())
        race_ergebnis, status2 = Spieler('Ergebnis').get_race_tipps(race_id)
        race_ergebnis = list(race_ergebnis.values())
        cityName = utils.get_cityName(race_id)['cityName']
        wmStand = list(wmStand[0].values())

        message = 'Alles ok'
        success = True
        if status1['success'] and status2['success']:


            for i, tipp in enumerate(racetipps):
                if tipp == race_ergebnis[i]:

                    if cityName == 'Melbourne':
                        rpunkte.update({f'rpunkte{i+1}': 10})
                    else:
                        if wmStand is not None and tipp in wmStand:
                            j = wmStand.index(tipp)
                            rpunkte.update({f'rpunkte{i+1}': abs(j - i) * 10 + 10})
                        else:
                            rpunkte.update({f'rpunkte{i+1}': 0})
                            message = 'Kein WM Stand vorhanden'
                            success = False

                elif tipp != race_ergebnis[i] and tipp in race_ergebnis:
                    if wmStand is not None and tipp in wmStand:
                        j = wmStand.index(tipp)
                        if abs(i - j) > 1:
                            rpunkte.update({f'rpunkte{i+1}': 5})
                        else:
                            rpunkte.update({f'rpunkte{i+1}': 8})
                    else:
                        if cityName == 'Melbourne':
                            rpunkte.update({f'rpunkte{i+1}': 5})
                        else:
                            rpunkte.update({f'rpunkte{i+1}': 0})
                            message = f'Kein WM Stand vorhanden oder {tipp} nicht in WM Liste'
                            success = False

                else:
                    rpunkte.update({f'rpunkte{i+1}': 0})
        if not status1['success']:
            message += f'Keine Racetipps für {self.name}.'
            success = False
        if not status2['success']:
            message += f' Noch kein Ergebnis eingetragen.'
            success = False

        status = {'success': success, 'message': message}
        return rpunkte, status


    def calculate_fastestLab_tipps(self, race_id):
        fastestLab_tipp, status1 = self.get_fastestlab_tipp(race_id)
        fastestLab_tipp = list(fastestLab_tipp.values())

        fastestLab_ergebnis, status2 = Spieler('Ergebnis').get_fastestlab_tipp(race_id)
        fastestLab_ergebnis = list(fastestLab_ergebnis.values())

        fastestlabpunkte = {}

        msg = ''
        success = True
        if status1['success'] and status2['success']:
            if fastestLab_tipp[0] == fastestLab_ergebnis[0]:
                fastestlabpunkte = {'fpunkte': 15}
            else:
                fastestlabpunkte = {'fpunkte': 0}
            msg = 'Alles ok'

        if not status1['success']:
            msg += f'Keine Qualitipps für {self.name}.'
            success = False
        if not status2['success']:
            msg += f' Noch kein Ergebnis eingetragen'
            success = False
        status = {'success': success, 'message': msg}

        return fastestlabpunkte, status



    def calculate_gesamtPunkte(self, punkte):

        quali_keys = ['qpunkte1', 'qpunkte2', 'qpunkte3', 'qpunkte4']
        race_keys = ['rpunkte1', 'rpunkte2', 'rpunkte3', 'rpunkte4', 'rpunkte5', 'rpunkte6', 'rpunkte7', 'rpunkte8',
                     'rpunkte9', 'rpunkte10']

        if punkte == {}:
            msg = f'Keine Punkte für {', '.join(self.name)}'
            return {}, {'success': False, 'message': msg}


        qPunkte = sum(punkte.get(qkey, 0) for qkey in quali_keys)
        rPunkte = sum(punkte.get(rkey, 0) for rkey in race_keys)
        fPunkte = punkte.get('fpunkte', 0)

        gesamtPunkte = qPunkte + rPunkte + fPunkte
        ergebnis = {
            'qPunkte': qPunkte,
            'rPunkte': rPunkte,
            'fPunkte': fPunkte,
            'gesamtPunkte': gesamtPunkte
        }

        msg = "Alles ok"

        status = {'success': True, 'message': msg}
        return ergebnis, status


    def get_sprint_tipps(self, race_id):
        ergebnis = {}
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT is_sprint FROM races WHERE id = %s", (race_id,))
        result = cursor.fetchall()[0][0]

        if result:
            cursor.execute("""
                        SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8
                        FROM sprinttipps
                        WHERE user_id = %s AND race_id = %s
                        ORDER BY id DESC LIMIT 1
                        """, (self.user_id, race_id))
            sresult = cursor.fetchone()

            ergebnis.update({f'sdriver{i + 1}': sresult[i] for i in range(len(sresult))})

        return ergebnis

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
        if qresult is None:
            msg = f'Keine Qualitipps für {self.name} in der Datenbank'
            return {}, {'success': False, 'message': msg} # Falls keine Daten vorhanden sind, gib ein leeres Dict zurück
        status = {'success': True, 'message': 'Alles ok'}
        return {f'qdriver{i + 1}': driver for i, driver in enumerate(qresult)}, status


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
        if rresult is None:
            msg = f'Keine Racetipps für {self.name} in der Datenbank'
            return {}, {'success': False, 'message': msg}

        status = {'success': True, 'message': 'Alles ok'}
        return {f'rdriver{i + 1}': driver for i, driver in enumerate(rresult)}, status


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

        if fresult is None:
            msg = f'Keine FastestLabTipp für {self.name} in der Datenbank'
            return {}, {'success': False, 'message': msg}

        status = {'success': True, 'message': 'Alles ok'}
        return {f'fdriver': fresult[0]}, status


    def set_quali_tipps(self, race_id, qdrivers):
        db = get_db()
        cursor = db.cursor()

        # 3. Daten in QualiTips speichern
        cursor.execute('''
                 INSERT INTO qualitipps (user_id, race_id, driver1, driver2, driver3, driver4)
                 VALUES (%s, %s, %s, %s, %s, %s)
         ''', (self.user_id, race_id, *qdrivers))
        db.commit()


    def set_race_tipps(self, race_id, rdrivers):
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
                        INSERT INTO racetipps (user_id, race_id, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10 )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (self.user_id, race_id, *rdrivers))
        db.commit()

    def set_fastestLab_tipps(self, race_id, fdriver):
        db = get_db()
        cursor = db.cursor()

        # 3. Daten in FastestLab speichern
        cursor.execute('''
                           INSERT INTO fastestlab (user_id, race_id, driver1)
                           VALUES (%s, %s, %s)
                   ''', (self.user_id, race_id, fdriver))
        db.commit()

    def set_sprint_tipps(self, race_id, sdrivers):
        db = get_db()
        cursor = db.cursor()

        # 3. Daten in QualiTips speichern
        cursor.execute('''
                    INSERT INTO sprinttipps (user_id, race_id, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (self.user_id, race_id, *sdrivers))
        db.commit()