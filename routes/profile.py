import psycopg2
from psycopg2.extras import RealDictCursor
from flask_login import login_required, current_user
from flask import render_template, Blueprint, session

from db import get_db

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
@login_required
def profile():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # 🔹 Tipprunden des aktuellen Users
    cursor.execute("""
                    SELECT t.id, t.name
                    FROM tipprunden t
                    JOIN tipprunden_user tu ON tu.tipprunde_id = t.id
                    WHERE tu.user_id = %s
                    ORDER BY t.name
                """, (current_user.id,))
    tipprunden = cursor.fetchall()

    # 🔹 Fall: User ist in keiner Tipprunde
    if not tipprunden:
        return render_template(
            "profile.html",
            tipprunden=[],
            users=[current_user],
            tipprunde_id=None
        )

    # 🔹 Fallback: erste Tipprunde
    tipprunde_id = session.get('tipprunde_id') or tipprunden[0]['id']

    # 🔹 User der aktiven Tipprunde
    cursor.execute("""
                    SELECT u.id, u.username
                    FROM users u
                    JOIN tipprunden_user tu ON tu.user_id = u.id
                    WHERE tu.tipprunde_id = %s
                    ORDER BY u.username
                """, (tipprunde_id,))
    users = cursor.fetchall()

    return render_template("profile.html",
                           tipprunden=tipprunden,
                           users=users,
                           tipprunde_id=tipprunde_id
                           )
