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
        if qresult is not None:
            ergebnis.update({f'qdriver{i + 1}': qresult[i] for i in range(len(qresult))})

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

        return ergebnis

    def get_sprint_tipps(self, race_id):
        ergebnis = {}
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
               SELECT driver1, driver2, driver3, driver4, driver5, driver6, driver7, driver8
               FROM sprinttipps
               WHERE user_id = %s AND race_id = %s
               ORDER BY id DESC LIMIT 1
           """, (self.user_id, race_id))

        sresult = cursor.fetchone()
        if sresult is not None:
            ergebnis.update({f'sdriver{i + 1}': sresult[i] for i in range(len(sresult))})

        return ergebnis

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