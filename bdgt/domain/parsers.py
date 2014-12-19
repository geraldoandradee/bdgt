import datetime
import csv
import os
import re
import tempfile

from mt940 import MT940
from namedlist import namedlist
from ofxparse import OfxParser as OfxLibParser


ParsedTransaction = namedlist('ParsedTransaction',
                              'date amount account description')


class TransactionParserFactory(object):
    @classmethod
    def create(cls, file_typetype):
        if file_typetype == 'csv_ing':
            return CsvIngParser()
        elif file_typetype == 'mt940':
            return Mt940Parser()
        elif file_typetype == 'ofx':
            return OfxParser()
        else:
            raise ValueError("Unknown type '{}'".format(file_typetype))


class Mt940Parser(object):
    def parse(self, file_type):
        mt940 = MT940(file_type)
        p_txs = []
        for f_stmt in mt940.statements:
            account_number = f_stmt.account.replace(' ', '')
            for f_tx in f_stmt.transactions:
                p_tx = ParsedTransaction(f_tx.booking, f_tx.amount,
                                         unicode(account_number),
                                         unicode(f_tx.description))
                p_txs.append(p_tx)
        return p_txs


class OfxParser(object):
    def parse(self, file_type):
        # ofxparse workaround
        # ofxparse doesn't parse the transaction amount correctly. It assumes
        # that the decimal point separator is always a full-stop; however, it
        # depends on the locale of the statement.
        #
        # This workaround finds the transaction amount in the file and replaces
        # comma with a full-stop. A temporary file is used to make the change
        # so the original file data stays intact.
        with open(file_type) as f:
            data = f.read()
        data = re.sub(r'<TRNAMT>([-\d]+),([\d]+)', r'<TRNAMT>\1.\2', data)

        ofx_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            with ofx_file as f:
                f.write(data)

            # Actual parsing
            ofx = OfxLibParser.parse(file(ofx_file.name))
            p_txs = []
            for f_acc in ofx.accounts:
                for f_tx in f_acc.statement.transactions:
                    p_tx = ParsedTransaction(
                        f_tx.date.date(), f_tx.amount,
                        unicode(f_acc.number).replace(' ', ''),
                        unicode(f_tx.memo))
                    p_txs.append(p_tx)
            return p_txs
        finally:
            os.remove(ofx_file.name)


class CsvIngParser(object):
    def parse(self, file_type):
        if not os.path.exists(file_type):
            raise ValueError("'{}' not found".format(file_type))

        with open(file_type, 'r') as f:
            csv_reader = csv.DictReader(f)
            p_txs = []
            for tx in csv_reader:
                # Parse the date. There are two formats: yyyymmdd and
                # dd-mm-yyyy.
                if '-' in tx['Datum']:
                    fmt = '%d-%m-%Y'
                else:
                    fmt = '%Y%m%d'
                tx_date = datetime.datetime.strptime(tx['Datum'], fmt).date()

                # Parse the amount. First assume that the decimal separator is
                # a '.'; otherwise, use ','.
                try:
                    tx_amount = float(tx['Bedrag (EUR)'])
                except ValueError:
                    tx_amount = float(tx['Bedrag (EUR)'].replace(',', '.'))
                if tx['Af Bij'] == 'Af':
                    tx_amount = -tx_amount

                tx_account = unicode(tx['Rekening']).replace(' ', '')
                tx_description = unicode(tx['Naam / Omschrijving'])
                tx_description += '\n' + unicode(tx['Mededelingen'])

                p_tx = ParsedTransaction(tx_date, tx_amount, tx_account,
                                         tx_description)
                p_txs.append(p_tx)
            return p_txs
