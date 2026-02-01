import psycopg2.extras
from flask import current_app
from db import get_db


class Dummytipps:
    """
    Verwaltung der Dummy-Tipps:
    - quali (driver1-4)
    - race (driver1-10)
    - sprint (driver1-8)
    - fastest lap (driver1)
    """

    def __init__(self):

        self.table_map = {
            "quali": ("dummy_quali_tipps", 4, 'qdriver'),
            "race": ("dummy_race_tipps", 10, 'rdriver'),
            "sprint": ("dummy_sprint_tipps", 8, 'sdriver'),
            "fastest": ("dummy_fastest_lab", 1, 'fdriver'),
        }

    def save_tipps(self, dummy_user_id, race_id, saison, tipps, tipp_type):
        """
        Speichert oder aktualisiert Dummy-Tipps.
        tipps: dict z.B. {"driver1": "Verstappen", ...}
        """
        if tipp_type not in self.table_map:
            raise ValueError(f"Unknown tip type: {tipp_type}")

        table, max_drivers, _ = self.table_map[tipp_type]
        placeholders = ", ".join([f"driver{i+1}" for i in range(max_drivers)])
        #values = [tipps.get(f"driver{i+1}") for i in range(max_drivers)]

        db = get_db()
        cursor = db.cursor()
        cursor.execute(f"""
            INSERT INTO {table} (user_id, race_id, saison, {placeholders}, created_at)
            VALUES (%s, %s, %s, {', '.join(['%s']*max_drivers)}, NOW())
            ON CONFLICT (user_id, race_id, saison)
            DO UPDATE SET {', '.join([f"driver{i+1} = EXCLUDED.driver{i+1}" for i in range(max_drivers)])},
            created_at = NOW();
        """, [dummy_user_id, race_id, saison, *tipps])

        db.commit()

    def get_tipps(self, dummy_user_id, race_ids, saison, tipp_type):
        """
        Gibt Dummy-Tipps für ein oder mehrere Rennen zurück.
        Rückgabe:
            {
                race_id: {driver1: ..., driver2: ...}
            }
        """
        if tipp_type not in self.table_map:
            raise ValueError(f"Unknown tip type: {tipp_type}")

        # einzelne ID erlauben
        if not isinstance(race_ids, (list, tuple)):
            race_ids = [race_ids]

        table, max_drivers, _ = self.table_map[tipp_type]

        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        driver_cols = ", ".join([f"{table}.driver{i + 1}" for i in range(max_drivers)])

        cursor.execute(f"""
            SELECT {table}.race_id, {driver_cols}
            FROM {table}
            JOIN users ON {table}.user_id = users.id
            WHERE {table}.race_id = ANY(%s)
              AND {table}.saison = %s
              AND {table}.user_id = %s
            ORDER BY {table}.id DESC
        """, (race_ids, saison, dummy_user_id))

        rows = cursor.fetchall()

        if not rows:
            return {}

        result = {}

        for row in rows:
            race_id = row.pop("race_id")

            # nur neuesten Eintrag je race behalten
            if race_id not in result:
                result[race_id] = dict(row)

        return result

    def get_tipps_for_frontend(self, dummy_user_id, race_id, saison, tipp_type):
        """
        Gibt Dummy-Tipps in Frontend-kompatibler Form zurück.
        Optional: hier kann man noch Punkte etc. berechnen
        """
        if tipp_type not in self.table_map:
            raise ValueError(f"Unknown tip type: {tipp_type}")

        table, max_drivers, driver = self.table_map[tipp_type]


        raw_tipps = self.get_tipps(dummy_user_id, [race_id], saison, tipp_type)
        raw_tipps = raw_tipps.get(race_id)

        if raw_tipps is None:
            return {}

        return {f"{driver}{i+1}": raw_tipps[f"driver{i+1}"] for i in range(self.table_map[tipp_type][1])}

