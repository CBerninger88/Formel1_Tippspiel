import psycopg2

from models.db import get_db
from psycopg2.extras import RealDictCursor

class Spieler:
    def __init__(self, name):
        """Konstruktor, der den Namen des Spielers speichert."""
        self.name = name
        self.user_id = self.get_user_id()

    def get_user_id(self):
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id FROM users WHERE username = %s', (self.name,))
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


    def calculate_gesamtPunkte(self, punkte):

        quali_keys = ['qpunkte1', 'qpunkte2', 'qpunkte3', 'qpunkte4']
        race_keys = ['rpunkte1', 'rpunkte2', 'rpunkte3', 'rpunkte4', 'rpunkte5', 'rpunkte6', 'rpunkte7', 'rpunkte8',
                     'rpunkte9', 'rpunkte10']

        if punkte == {}:
            namen_liste = ', '.join(self.name)
            msg = f'Keine Punkte für {namen_liste}'
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

    def get_sprint_tipps(self, race_ids, tipprunde_id):
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # einzelne ID erlauben
        if not isinstance(race_ids, (list, tuple)):
            race_ids = [race_ids]

        cursor.execute("""
            SELECT DISTINCT ON (t.race_id)
                t.race_id,
                t.driver1, t.driver2, t.driver3, t.driver4,
                t.driver5, t.driver6, t.driver7, t.driver8
            FROM sprinttipps t
            JOIN races r ON r.id = t.race_id
            WHERE t.user_id = %s
              AND t.tipprunde_id = %s
              AND t.race_id = ANY(%s)
              AND r.is_sprint = TRUE
            ORDER BY t.race_id, t.id DESC
        """, (self.user_id, tipprunde_id, race_ids))

        rows = cursor.fetchall()

        if not rows:
            msg = f'Keine Sprinttipps für {self.name} in Tipprunde {tipprunde_id}'
            return {}, {'success': False, 'message': msg}

        result = {}

        for row in rows:
            race_id = row.pop("race_id")
            result[race_id] = {f"s{k}": v for k, v in row.items()}

        return result, {'success': True, 'message': 'Alles ok'}

    def get_quali_tipps(self, race_ids, tipprunde_id):
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT DISTINCT ON (race_id)
                race_id,
                driver1, driver2, driver3, driver4
            FROM qualitipps
            WHERE user_id = %s
              AND race_id = ANY(%s)
              AND tipprunde_id = %s
            ORDER BY race_id, id DESC
        """

        cursor.execute(query, (self.user_id, race_ids, tipprunde_id))
        results = cursor.fetchall()

        if not results:
            msg = f'Keine Qualitipps für {self.name} in Tipprunde {tipprunde_id}'
            return {}, {'success': False, 'message': msg}

        data = {}

        for row in results:
            race_id = row["race_id"]
            data[race_id] = {f"qdriver{i + 1}": row[f"driver{i + 1}"] for i in range(4)}

        return data, {'success': True, 'message': 'Alles ok'}

    def get_race_tipps(self, race_ids, tipprunde_id):
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT DISTINCT ON (race_id)
                race_id,
                driver1, driver2, driver3, driver4, driver5,
                driver6, driver7, driver8, driver9, driver10
            FROM racetipps
            WHERE user_id = %s
              AND race_id = ANY(%s)
              AND tipprunde_id = %s
            ORDER BY race_id, id DESC
        """

        cursor.execute(query, (self.user_id, race_ids, tipprunde_id))
        results = cursor.fetchall()

        if not results:
            msg = f'Keine Racetipps für {self.name} in Tipprunde {tipprunde_id}'
            return {}, {'success': False, 'message': msg}

        data = {}

        for row in results:
            race_id = row["race_id"]

            data[race_id] = {
                f"rdriver{i + 1}": row[f"driver{i + 1}"]
                for i in range(10)
            }

        return data, {'success': True, 'message': 'Alles ok'}

    def get_fastestlap_tipp(self, race_ids, tipprunde_id):
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT DISTINCT ON (race_id)
                race_id, driver1
            FROM fastestlab
            WHERE user_id = %s
              AND race_id = ANY(%s)
              AND tipprunde_id = %s
            ORDER BY race_id, id DESC
        """

        cursor.execute(query, (self.user_id, race_ids, tipprunde_id))
        results = cursor.fetchall()

        if not results:
            msg = f'Keine FastestLapTipps für {self.name} in Tipprunde {tipprunde_id}'
            return {}, {'success': False, 'message': msg}

        data = {}

        for row in results:
            race_id = row["race_id"]
            data[race_id] = {"fdriver1": row["driver1"]}

        return data, {'success': True, 'message': 'Alles ok'}

    def set_quali_tipps(self, race_id, qdrivers, tipprunde_id):
        db = get_db()
        cursor = db.cursor()

        # 3. Daten in QualiTips speichern
        cursor.execute('''
                 INSERT INTO qualitipps (user_id, race_id, driver1, driver2, driver3, driver4, tipprunde_id, created_at)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, Now())
         ''', (self.user_id, race_id, *qdrivers, tipprunde_id))
        db.commit()


    def set_race_tipps(self, race_id, rdrivers, tipprunde_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
                        INSERT INTO racetipps (user_id, race_id, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, driver9, driver10, tipprunde_id, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, Now())
                ''', (self.user_id, race_id, *rdrivers, tipprunde_id))
        db.commit()

    def set_fastestLab_tipps(self, race_id, fdriver, tipprunde_id):
        db = get_db()
        cursor = db.cursor()

        driver = fdriver if fdriver else ''

        # 3. Daten in FastestLab speichern
        cursor.execute('''
                           INSERT INTO fastestlab (user_id, race_id, driver1, tipprunde_id, created_at)
                           VALUES (%s, %s, %s, %s, Now())
                   ''', (self.user_id, race_id, driver, tipprunde_id))
        db.commit()

    def set_sprint_tipps(self, race_id, sdrivers, tipprunde_id):
        db = get_db()
        cursor = db.cursor()

        # 3. Daten in SprintTipps speichern
        cursor.execute('''
                    INSERT INTO sprinttipps (user_id, race_id, driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8, tipprunde_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,NOW())
            ''', (self.user_id, race_id, *sdrivers, tipprunde_id))
        db.commit()