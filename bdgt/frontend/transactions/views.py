import logging

from flask import Blueprint, flash, g, render_template, request, url_for
from sqlalchemy.sql.expression import not_

from bdgt import db
from bdgt.domain.models import Account, Category, Transaction


_log = logging.getLogger(__name__)

bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@bp.route("/", methods=['GET'])
def list():
    query = Transaction.query

    q = request.args.get('q', '')
    if q != '':
        filters = q.split(' ')
        for f in filters:
            if ':' in f:
                exp = f.split(':')
                context = exp[0]
                stmt = exp[1]

                cpt = '=='
                if stmt[0] == '>':
                    if stmt[1] == '=':
                        cpt = '>='
                        stmt = stmt[2:]
                    else:
                        cpt = '>'
                        stmt = stmt[1:]
                elif stmt[0] == '<':
                    if stmt[1] == '=':
                        cpt = '<='
                        stmt = stmt[2:]
                    else:
                        cpt = '<'
                        stmt = stmt[1:]

                if context == "is":
                    if not hasattr(Transaction, stmt):
                        flash("{} is not a valid filter".format(f), 'warning')
                    else:
                        query = query.filter(getattr(Transaction, stmt))
                elif context == "not":
                    if not hasattr(Transaction, stmt):
                        flash("{} is not a valid filter".format(f), 'warning')
                    else:
                        query = query.filter(not_(getattr(Transaction, stmt)))
                elif context == "account":
                    query = query.join(Account).filter(Account.name == stmt)
                elif context == "amount":
                    query = query.filter(Transaction.amount.op(
                        cpt, is_comparison=True)(stmt))
                elif context == "date":
                    query = query.filter(Transaction.date.op(
                        cpt, is_comparison=True)(stmt))
                elif context == "category":
                    query = query.join(Category).filter(Category.name == stmt)
                else:
                    flash("{} is not a valid filter".format(f), 'warning')
            else:
                query = query.filter(Transaction.description.contains(f))

    page = int(request.args.get('page', 1))
    tx_pages = query.order_by(Transaction.date.desc()).paginate(page, 20)

    root_categories = Category.query.filter_by(parent_id=None).all()

    return render_template("transactions/index.html", tx_pages=tx_pages, q=q,
                           categories=root_categories)


@bp.route("/set_category", methods=['POST'])
def set_category():
    cat_id = request.json.get('cat_id')
    tx_ids = request.json.get('tx_ids')

    category = Category.query.get(cat_id)
    txs = Transaction.query.filter(Transaction.id.in_(tx_ids)).all()
    for tx in txs:
        tx.category = category
    db.session.commit()

    return "ok"


@bp.route("/set_reconciled", methods=['POST'])
def set_reconciled():
    reconciled = request.json.get('reconciled')
    tx_ids = request.json.get('tx_ids')

    txs = Transaction.query.filter(Transaction.id.in_(tx_ids)).all()
    for tx in txs:
        tx.reconciled = reconciled
    db.session.commit()

    return "ok"


@bp.route("/delete", methods=['POST'])
def delete():
    tx_ids = request.json.get('tx_ids')

    txs = Transaction.query.filter(Transaction.id.in_(tx_ids)).all()
    for tx in txs:
        db.session.delete(tx)
    db.session.commit()

    return "ok"


@bp.before_request
def before_request():
    g.section = 'transactions'


def url_for_page(page):
    args = request.args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
