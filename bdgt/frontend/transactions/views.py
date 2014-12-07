import logging

from flask import Blueprint, g, render_template, request

from bdgt.domain.models import Account, Transaction


_log = logging.getLogger(__name__)

bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@bp.route("/", methods=['GET'])
def list():
    account_number = request.args.get('account', None)
    if account_number:
        txs_query = Transaction.query.join(Account).filter(
            Account.number == account_number)
    else:
        txs_query = Transaction.query

    txs = txs_query.all()

    return render_template("transactions/index.html", txs=txs)


@bp.before_request
def before_request():
    g.section = 'transactions'
