import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_mail import Message, Mail
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from models.db import get_db
from models.user import User
from itsdangerous import URLSafeTimedSerializer



auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

mail = Mail()

def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):

            # 🔹 Tipprunden des aktuellen Users
            cursor.execute("""
                            SELECT t.id, t.name
                            FROM tipprunden t
                            JOIN tipprunden_user tu ON tu.tipprunde_id = t.id
                            WHERE tu.user_id = %s
                            ORDER BY t.name
                        """, (user['id'],))
            tipprunden = cursor.fetchall()

            if tipprunden:
                session['tipprunde_id'] = tipprunden[0]['id']
            else:
                session['tipprunde_id'] = None

            login_user(User(user["id"], user["username"], user["password_hash"]))
            return redirect(url_for("home.index"))
        else:
            flash("Benutzername oder Passwort falsch")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home.index"))


#@auth_bp.route('/register')
#def register():
#    return render_template('register.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']


        # 1️⃣ Passwörter prüfen
        if password != confirm_password:
            flash("Passwörter stimmen nicht überein")
            return render_template('register.html')

        db = get_db()

        # 2️⃣ Prüfen, ob Username schon existiert
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Benutzername oder E-mail existiert bereits")
            return render_template('register.html')

        # 3️⃣ Passwort hashen
        password_hash = generate_password_hash(password)

        # 4️⃣ User speichern
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (username, email, password_hash)
        )

        db.commit()

        flash("Registrierung erfolgreich – bitte einloggen")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if user:
            serializer = get_serializer()
            token = serializer.dumps(
                user["email"],
                salt="password-reset"
            )

            reset_url = url_for(
                "auth.reset_password",
                token=token,
                _external=True
            )

            # 🔧 Fürs Testen verständlich & praktisch
            send_reset_email(user["email"], user['username'], reset_url)
            print("PASSWORT-RESET-LINK:", reset_url)

        flash("Falls ein Konto mit dieser E-Mail existiert, wurde ein Reset-Link erzeugt.")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    serializer = get_serializer()

    try:
        email = serializer.loads(
            token,
            salt="password-reset",
            max_age=1800
        )
    except Exception:
        flash("Der Link ist ungültig oder abgelaufen.")
        return redirect(url_for("auth.login"))

    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )
    user = cursor.fetchone()

    if not user:
        flash("Benutzer nicht gefunden.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        new_password = request.form["password"]
        password_hash = generate_password_hash(new_password)

        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (password_hash, user["id"])
        )
        db.commit()

        flash("Passwort erfolgreich geändert.")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")





def send_reset_email(to_email, username, reset_url):
    msg = Message(
        subject="Passwort zurücksetzen – Formel 1 Tippspiel",
        recipients=[to_email],
        body=f"""
Hallo,

dein Benutzername lautet: {username}

Klicke auf den folgenden Link, um dein Passwort zurückzusetzen:

{reset_url}

Der Link ist 30 Minuten gültig.

Wenn du diese E-Mail nicht angefordert hast, ignoriere sie bitte.
"""
    )
    mail.send(msg)

