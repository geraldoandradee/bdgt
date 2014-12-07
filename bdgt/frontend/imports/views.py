import logging
import os

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from werkzeug.utils import secure_filename

from bdgt.domain.imports import import_transactions
from bdgt.frontend.imports.forms import TransactionImportForm


_log = logging.getLogger(__name__)

bp = Blueprint('imports', __name__, url_prefix='/import')


@bp.route("/", methods=['GET', 'POST'])
def form():
    form = TransactionImportForm()
    if form.validate_on_submit():
        # Save the uploaded transaction file
        txs_file = request.files['txs_file']
        filename = os.path.join('/tmp', secure_filename(txs_file.name))
        txs_file.save(filename)

        # Import the transactions
        imported_txs = import_transactions(filename, form.file_type.data)

        flash("Imported {} transactions".format(len(imported_txs)))

        return redirect(url_for('dashboard.index'))
    return render_template('form.html', form=form,
                           form_title="Import Transactions",
                           action_url=url_for('imports.form'),
                           enctype='multipart/form-data')


@bp.before_request
def before_request():
    g.section = 'imports'


@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    _log.error("Unhandled exception: {}".format(error))
    return render_template('imports/error.html', msg=error), 500
