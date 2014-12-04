import logging

from flask import Blueprint, redirect, render_template, url_for

from bdgt import db
from bdgt.domain.models import Account
from bdgt.frontend.accounts.forms import AccountForm


_log = logging.getLogger(__name__)

bp = Blueprint('accounts', __name__)


@bp.route("/accounts", methods=['GET'])
def index():
    accounts = Account.query.all()
    return render_template("accounts/index.html", accounts=accounts)


@bp.route("/accounts/new", methods=['GET', 'POST'])
def new():
    form = AccountForm()
    if form.validate_on_submit():
        account = Account(form.name.data, form.number.data)
        db.session.add(account)
        db.session.commit()

        return redirect(url_for('accounts.index'))
    return render_template('form.html', form=form, form_title="Add Account",
                           action_url=url_for('accounts.index'))
