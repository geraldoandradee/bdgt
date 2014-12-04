import logging

from flask import Blueprint, render_template

from bdgt.domain.models import Account


_log = logging.getLogger(__name__)

bp = Blueprint('txs', __name__, url_prefix='/transactions')


@bp.route("/<account_name>", methods=['GET'])
def index(account_name):
    account = Account.query.filter_by(name=account_name).one()

    return render_template("transactions/index.html", txs=account.transactions)
