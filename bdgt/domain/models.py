from sqlalchemy.orm import backref

from bdgt import db


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False, unique=True)
    number = db.Column(db.Unicode, nullable=False)
    transactions = db.relationship("Transaction", backref="account",
                                   cascade='all, delete, delete-orphan')

    def __init__(self, name, number):
        self.name = name
        self.number = number


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name = db.Column(db.Unicode, nullable=False)
    subcategories = db.relationship("Category",
                                    backref=backref('parent',
                                                    remote_side=[id]),
                                    cascade="all, delete-orphan")

    def __repr__(self):
        return self.name


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Unicode)
    amount = db.Column(db.Float, nullable=False)
    reconciled = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship("Category", backref="transactions")

    def __init__(self, account, date, description, amount,
                 reconciled=False):
        self.account = account
        self.date = date
        self.description = description
        self.amount = amount
        self.reconciled = reconciled

    def is_credit(self):
        return self.amount > 0

    def is_debit(self):
        return self.amount < 0
