import datetime
import os
import tempfile
from decimal import Decimal

from mock import patch
from nose.tools import eq_, ok_, raises

from bdgt.domain.parsers import (CsvIngParser, Mt940Parser,
                                 TransactionParserFactory, OfxParser)


def test_tx_parser_factory():
    parser = TransactionParserFactory.create("mt940")
    ok_(isinstance(parser, Mt940Parser))


@raises(ValueError)
def test_tx_parser_factory_unknown_type():
    TransactionParserFactory.create("unknown")


@patch('os.path.exists', return_value=True)
def test_parse_mt940(mock_exists):
    txs_data = "ABNANL2A\n" + \
               "940\n" + \
               "ABNANL2A\n" + \
               ":20:ABN AMRO BANK NV\n" + \
               ":25:987654321\n" + \
               ":28:13501/1\n" + \
               ":60F:C120511EUR5138,61\n" + \
               ":61:1705120512C500,01N654NONREF\n" + \
               ":86:/TRTP/SEPA OVERBOEKING/IBAN/FR12345678901234/BIC/" + \
               "GEFRADAM /NAME/QASD JGRED/REMI/description lines/EREF/" + \
               "NOTPRO VIDED\n" + \
               ":62F:C120514EUR5638,62\n"
    data_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        with data_file as f:
            f.write(txs_data)

        parser = Mt940Parser()
        txs = parser.parse(data_file.name)

        eq_(len(txs), 1)
        eq_(txs[0].date, datetime.date(2017, 5, 12))
        eq_(txs[0].amount, Decimal('500.01'))
        eq_(txs[0].account, u'987654321')
        eq_(txs[0].description, u'/TRTP/SEPA OVERBOEKING/IBAN/' +
                                u'FR12345678901234/BIC/GEFRADAM ' +
                                u'/NAME/QASD JGRED/REMI/' +
                                u'description lines/EREF/NOTPRO VIDED')

        ok_(type(txs[0].account) == unicode)
        ok_(type(txs[0].description) == unicode)
    finally:
        os.remove(data_file.name)


@patch('os.path.exists', return_value=True)
def test_parse_mt940_valid_account_number(mock_exists):
    """
    Tests that the parser parses the account number correctly.
    """
    txs_data = "ABNANL2A\n" + \
               "940\n" + \
               "ABNANL2A\n" + \
               ":20:ABN AMRO BANK NV\n" + \
               ":25:98765 4321\n" + \
               ":28:13501/1\n" + \
               ":60F:C120511EUR5138,61\n" + \
               ":61:1705120512C500,01N654NONREF\n" + \
               ":86:/TRTP/SEPA OVERBOEKING/IBAN/FR12345678901234/BIC/" + \
               "GEFRADAM /NAME/QASD JGRED/REMI/description lines/EREF/" + \
               "NOTPRO VIDED\n" + \
               ":62F:C120514EUR5638,62\n"
    data_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        with data_file as f:
            f.write(txs_data)

        parser = Mt940Parser()
        txs = parser.parse(data_file.name)
        eq_(txs[0].account, u'987654321')
    finally:
        os.remove(data_file.name)


@patch('os.path.exists', return_value=True)
def test_parse_csv_ing(mock_exists):
    txs_data = '"Datum","Naam / Omschrijving","Rekening","Tegenrekening",' +\
               '"Code","Af Bij","Bedrag (EUR)","MutatieSoort",' +\
               '"Mededelingen"\n' + \
               '"20150801","Naam en omsch.","987654321","11112222","BA",' +\
               '"Af","12,75","Betaalautomaat","Mededelingen hier"\n' + \
               '"20150802","Naam en omsch.","987654321","12321232","GT",' +\
               '"Bij","8,50","Internetbankieren","Mededelingen hier"'

    data_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        with data_file as f:
            f.write(txs_data)

        parser = CsvIngParser()
        txs = parser.parse(data_file.name)

        eq_(len(txs), 2)
        eq_(txs[0].date, datetime.date(2015, 8, 1))
        eq_(txs[0].amount, -12.75)
        eq_(txs[0].account, '987654321')
        eq_(txs[0].description, 'Naam en omsch.\nMededelingen hier')
        eq_(txs[1].date, datetime.date(2015, 8, 2))
        eq_(txs[1].amount, 8.50)
        eq_(txs[1].account, '987654321')
        eq_(txs[1].description, 'Naam en omsch.\nMededelingen hier')

        ok_(type(txs[0].account) == unicode)
        ok_(type(txs[0].description) == unicode)
    finally:
        os.remove(data_file.name)


@patch('os.path.exists', return_value=True)
def test_parse_csv_ing_valid_account_number(mock_exists):
    txs_data = '"Datum","Naam / Omschrijving","Rekening","Tegenrekening",' +\
               '"Code","Af Bij","Bedrag (EUR)","MutatieSoort",' +\
               '"Mededelingen"\n' + \
               '"20150801","Naam en omsch.","987 654321","11112222","BA",' +\
               '"Af","12,75","Betaalautomaat","Mededelingen hier"\n' + \
               '"20150802","Naam en omsch.","9876543 21","12321232","GT",' +\
               '"Bij","8,50","Internetbankieren","Mededelingen hier"'

    data_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        with data_file as f:
            f.write(txs_data)

        parser = CsvIngParser()
        txs = parser.parse(data_file.name)
        eq_(txs[0].account, '987654321')
        eq_(txs[1].account, '987654321')
    finally:
        os.remove(data_file.name)


def test_parse_ofx():
    ofx_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        with ofx_file as f:
            f.write("""
            <OFX>
                <SIGNONMSGSRSV1>
                <SONRS>
                    <STATUS>
                    <CODE>0
                    <SEVERITY>INFO
                    </STATUS>
                    <DTSERVER>20071015021529.000[-8:PST]
                    <LANGUAGE>ENG
                    <DTACCTUP>19900101000000
                    <FI>
                    <ORG>MYBANK
                    <FID>01234
                    </FI>
                </SONRS>
                </SIGNONMSGSRSV1>
                <BANKMSGSRSV1>
                    <STMTTRNRS>
                    <TRNUID>23382938
                    <STATUS>
                        <CODE>0
                        <SEVERITY>INFO
                    </STATUS>
                    <STMTRS>
                        <CURDEF>USD
                        <BANKACCTFROM>
                        <BANKID>987654321
                        <ACCTID>098-121
                        <ACCTTYPE>SAVINGS
                        </BANKACCTFROM>
                        <BANKTRANLIST>
                        <DTSTART>20070101
                        <DTEND>20071015
                        <STMTTRN>
                            <TRNTYPE>CREDIT
                            <DTPOSTED>20070315
                            <DTUSER>20070315
                            <TRNAMT>200.00
                            <FITID>980315001
                            <NAME>DEPOSIT
                            <MEMO>description lines
                        </STMTTRN>
                        </BANKTRANLIST>
                        <LEDGERBAL>
                        <BALAMT>5250.00
                        <DTASOF>20071015021529.000[-8:PST]
                        </LEDGERBAL>
                        <AVAILBAL>
                        <BALAMT>5250.00
                        <DTASOF>20071015021529.000[-8:PST]
                        </AVAILBAL>
                    </STMTRS>
                    </STMTTRNRS>
                </BANKMSGSRSV1>
            </OFX>
            """)
        parser = OfxParser()
        txs = parser.parse(ofx_file.name)
        eq_(len(txs), 1)
        eq_(txs[0].date, datetime.date(2007, 3, 15))
        eq_(txs[0].account, '098-121')
        ok_('description lines' in txs[0].description)
        eq_(txs[0].amount, Decimal('200.00'))
    finally:
        os.remove(ofx_file.name)


def test_parse_ofx_valid_account_number():
    ofx_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        with ofx_file as f:
            f.write("""
            <OFX>
                <SIGNONMSGSRSV1>
                <SONRS>
                    <STATUS>
                    <CODE>0
                    <SEVERITY>INFO
                    </STATUS>
                    <DTSERVER>20071015021529.000[-8:PST]
                    <LANGUAGE>ENG
                    <DTACCTUP>19900101000000
                    <FI>
                    <ORG>MYBANK
                    <FID>01234
                    </FI>
                </SONRS>
                </SIGNONMSGSRSV1>
                <BANKMSGSRSV1>
                    <STMTTRNRS>
                    <TRNUID>23382938
                    <STATUS>
                        <CODE>0
                        <SEVERITY>INFO
                    </STATUS>
                    <STMTRS>
                        <CURDEF>USD
                        <BANKACCTFROM>
                        <BANKID>987654321
                        <ACCTID>09 8-121
                        <ACCTTYPE>SAVINGS
                        </BANKACCTFROM>
                        <BANKTRANLIST>
                        <DTSTART>20070101
                        <DTEND>20071015
                        <STMTTRN>
                            <TRNTYPE>CREDIT
                            <DTPOSTED>20070315
                            <DTUSER>20070315
                            <TRNAMT>200.00
                            <FITID>980315001
                            <NAME>DEPOSIT
                            <MEMO>description lines
                        </STMTTRN>
                        </BANKTRANLIST>
                        <LEDGERBAL>
                        <BALAMT>5250.00
                        <DTASOF>20071015021529.000[-8:PST]
                        </LEDGERBAL>
                        <AVAILBAL>
                        <BALAMT>5250.00
                        <DTASOF>20071015021529.000[-8:PST]
                        </AVAILBAL>
                    </STMTRS>
                    </STMTTRNRS>
                </BANKMSGSRSV1>
            </OFX>
            """)
        parser = OfxParser()
        txs = parser.parse(ofx_file.name)
        eq_(txs[0].account, '098-121')
    finally:
        os.remove(ofx_file.name)
