from flask import Blueprint, render_template
from flask_login import current_user, login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def home():
    return render_template("dashboard.html", username=current_user.username)
