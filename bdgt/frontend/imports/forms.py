from flask_wtf import Form
from wtforms.fields import FileField, SelectField


class TransactionImportForm(Form):
    txs_file = FileField(u'File')
    file_type = SelectField(u'Type',
                            choices=[('csv_ing', 'CSV (ING)'),
                                     ('mt940', 'MT940'),
                                     ('ofx', 'OFX')])
