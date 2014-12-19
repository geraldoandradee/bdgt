import datetime

from nose.tools import eq_

from bdgt.domain.models import Account, Transaction


def test_is_debit():
    account = Account(u"test", u"12345")
    tx = Transaction(account, datetime.datetime.now(), u"desc", 10.0)
    eq_(tx.is_debit(), False)

    tx = Transaction(account, datetime.datetime.now(), u"desc", -10.0)
    eq_(tx.is_debit(), True)

    tx = Transaction(account, datetime.datetime.now(), u"desc", 0.0)
    eq_(tx.is_debit(), False)


def test_is_credit():
    account = Account(u"test", u"12345")
    tx = Transaction(account, datetime.datetime.now(), u"desc", 10.0)
    eq_(tx.is_credit(), True)

    tx = Transaction(account, datetime.datetime.now(), u"desc", -10.0)
    eq_(tx.is_credit(), False)

    tx = Transaction(account, datetime.datetime.now(), u"desc", 0.0)
    eq_(tx.is_credit(), False)
