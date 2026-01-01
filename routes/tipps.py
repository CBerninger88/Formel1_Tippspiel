import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from db import get_db


tipps_bp = Blueprint('tipps', __name__)

@tipps_bp.route("/tipps/<int:tipprunde_id>/", defaults={"rennen_id": None})
@tipps_bp.route("/tipps/<int:tipprunde_id>/<int:rennen_id>")
@login_required
def show_tipps(tipprunde_id, rennen_id):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Alle User in dieser Tipprunde holen
    cursor.execute("""
        SELECT u.id, u.username
        FROM users u
        JOIN tipprunden_user tu ON tu.user_id = u.id
        WHERE tu.tipprunde_id = %s
        ORDER BY u.username
    """, (tipprunde_id,))
    users = cursor.fetchall()  # Liste von Dicts: [{'id': 1, 'username': 'Alexander'}, ...]

    user_ids = [u['id'] for u in users]

    # QUALI Tipps
    cursor.execute("""
            SELECT DISTINCT ON (user_id) user_id, driver1, driver2, driver3, driver4
            FROM qualitipps
            WHERE tipprunde_id = %s AND race_id = %s AND user_id = ANY(%s)
            ORDER BY user_id, created_at DESC
        """, (tipprunde_id, rennen_id, user_ids))
    quali_tipps = cursor.fetchall()

    # RACE Tipps
    cursor.execute("""
            SELECT DISTINCT ON (user_id) user_id, driver1, driver2, driver3
            FROM racetipps
            WHERE tipprunde_id = %s AND race_id = %s AND user_id = ANY(%s)
            ORDER BY user_id, created_at DESC
        """, (tipprunde_id, rennen_id, user_ids))
    race_tipps = cursor.fetchall()

    # SPRINT Tipps
    cursor.execute("""
        SELECT DISTINCT ON (user_id) user_id, driver1, driver2, driver3
        FROM sprinttipps
        WHERE tipprunde_id = %s AND race_id = %s AND user_id = ANY(%s)
        ORDER BY user_id, created_at DESC
    """, (tipprunde_id, rennen_id, user_ids))
    sprint_tipps = cursor.fetchall()

    # FASTEST Runde
    cursor.execute("""
        SELECT DISTINCT ON (user_id) user_id, driver1
        FROM fastestlab
        WHERE tipprunde_id = %s AND race_id = %s AND user_id = ANY(%s)
        ORDER BY user_id, created_at DESC
    """, (tipprunde_id, rennen_id, user_ids))
    fastestrunde_tipps = cursor.fetchall()

    # Optional: Usernamen holen
    #users = {u['id']: u['username'] for u in cursor.execute("SELECT id, username FROM users").fetchall()}

    return render_template(
        "home.html",
        users=users,
        quali_tipps=quali_tipps,
        race_tipps=race_tipps,
        sprint_tipps=sprint_tipps,
        fastestrunde_tipps=fastestrunde_tipps,
    )
