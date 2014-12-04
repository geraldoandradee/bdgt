import logging
import os

from sqlalchemy.orm.exc import NoResultFound

from bdgt import db
from bdgt.domain.models import Account, Transaction
from bdgt.domain.parsers import TransactionParserFactory


_log = logging.getLogger(__name__)


def import_transactions(filename, file_type):
    if not os.path.exists(filename):
        raise ValueError("'{}' not found".format(filename))

    # Parse the transactions from the file
    parser = TransactionParserFactory.create(file_type)
    p_txs = parser.parse(filename)

    _log.info("Parsed {} transactions from '{}'".format(len(p_txs), filename))

    # Add them to the database with the imported field set to False
    txs = []
    for p_tx in p_txs:
        try:
            account = Account.query.filter_by(number=p_tx.account).one()
        except NoResultFound:
            _log.info("Creating account '{}'".format(p_tx.account))
            account = Account(p_tx.account, p_tx.account)
            db.session.add(account)

        tx = Transaction(account, p_tx.date, p_tx.description, p_tx.amount)
        txs.append(tx)
        db.session.add(tx)
    db.session.commit()

    return txs
