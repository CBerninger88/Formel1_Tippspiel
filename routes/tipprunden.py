from psycopg2.errors import UniqueViolation
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db

tipprunden_bp = Blueprint("tipprunden", __name__, url_prefix="/tipprunden")

@tipprunden_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        name = request.form["name"]
        join_password = request.form["join_password"]

        if not name or not join_password:
            flash("Name und Passwort sind erforderlich.")
            return redirect(url_for("tipprunden.create"))

        password_hash = generate_password_hash(join_password)

        conn = get_db()
        cur = conn.cursor()

        try:
            # 1️⃣ Tipprunde anlegen
            cur.execute(
                """
                INSERT INTO tipprunden (name, join_password_hash, created_by, created_at)
                VALUES (%s, %s, %s, NOW())
                RETURNING id
                """,
                (name, password_hash, current_user.id)
            )

            tipprunde_id = cur.fetchone()[0]

            # 2️⃣ Ersteller als Admin hinzufügen
            cur.execute(
                """
                INSERT INTO tipprunden_user (user_id, tipprunde_id, role)
                VALUES (%s, %s, 'admin')
                """,
                (current_user.id, tipprunde_id)
            )

            # 3️⃣ Dummy-User IDs laden
            cur.execute(
                """
                SELECT id
                FROM users
                WHERE username IN ('Dummy_WM', 'Dummy_LR', 'Dummy_LY', 'Dummy_Kon','Ergebnis')
                """
            )
            dummy_user_ids = [row[0] for row in cur.fetchall()]

            # 4️⃣ Dummy-User als Member hinzufügen
            cur.executemany(
                """
                INSERT INTO tipprunden_user (user_id, tipprunde_id, role)
                VALUES (%s, %s, 'member')
                """,
                [(user_id, tipprunde_id) for user_id in dummy_user_ids]
            )

            conn.commit()

            flash("✅ Tipprunde erfolgreich erstellt!")
            return redirect(url_for("tipprunden.create"))

        except UniqueViolation:
            conn.rollback()
            flash("❌ Eine Tipprunde mit diesem Namen existiert bereits.")

        finally:
            cur.close()

    return render_template("create_tipprunde.html")


@tipprunden_bp.route("/join", methods=["GET", "POST"])
@login_required
def join():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()

        # 1️⃣ Tipprunde suchen
        cur.execute(
            """
            SELECT id, join_password_hash
            FROM tipprunden
            WHERE name = %s
            """,
            (name,)
        )
        tipprunde = cur.fetchone()

        if tipprunde is None:
            flash("❌ Tipprunde nicht gefunden.")
            cur.close()
            return render_template("join_tipprunde.html")

        tipprunde_id, password_hash = tipprunde

        # 2️⃣ Passwort prüfen
        if not check_password_hash(password_hash, password):
            flash("❌ Falsches Passwort.")
            cur.close()
            return render_template("join_tipprunde.html")

        # 3️⃣ User zur Tipprunde hinzufügen
        try:
            cur.execute(
                """
                INSERT INTO tipprunden_user (tipprunde_id, user_id)
                VALUES (%s, %s)
                """,
                (tipprunde_id, current_user.id)
            )
            db.commit()
            flash("✅ Erfolgreich der Tipprunde beigetreten!")
            cur.close()
            return redirect(url_for("profile.profile"))

        except UniqueViolation:
            db.rollback()
            flash("ℹ️ Du bist bereits Mitglied dieser Tipprunde.")
            cur.close()

    return render_template("join_tipprunde.html")