import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from db import get_db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

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
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 1️⃣ Passwörter prüfen
        if password != confirm_password:
            flash("Passwörter stimmen nicht überein")
            return render_template('register.html')

        db = get_db()

        # 2️⃣ Prüfen, ob Username schon existiert
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Benutzername existiert bereits")
            return render_template('register.html')

        # 3️⃣ Passwort hashen
        password_hash = generate_password_hash(password)

        # 4️⃣ User speichern
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        db.commit()

        flash("Registrierung erfolgreich – bitte einloggen")
        return redirect(url_for('auth.login'))

    return render_template('register.html')