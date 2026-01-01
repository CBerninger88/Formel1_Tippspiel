from flask import Blueprint, render_template
from flask_login import login_required
from models.decorator import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/rennergebnisse")
@login_required
@admin_required
def rennergebnisse():
    return render_template("admin/rennergebnisse.html")


@admin_bp.route("/races")
@login_required
@admin_required
def races():
    return render_template("admin/races.html")


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    return render_template("admin/users.html")
