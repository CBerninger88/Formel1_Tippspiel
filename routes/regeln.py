import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, session
from flask_login import current_user
from models.db import get_db

regeln_bp = Blueprint('regeln', __name__)

@regeln_bp.route('/regeln')
def regeln():
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
            "regeln.html",
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

    return render_template("regeln.html",
                           tipprunden=tipprunden,
                           users=users,
                           tipprunde_id=tipprunde_id
                           )