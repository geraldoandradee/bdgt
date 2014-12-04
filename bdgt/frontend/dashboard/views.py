import logging

from flask import Blueprint, render_template


_log = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__)


@bp.route("/", methods=['GET'])
def index():
    return render_template("dashboard/index.html")
