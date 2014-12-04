from flask_wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form

from bdgt.domain.models import Account


AccountForm = model_form(Account, base_class=Form, exclude=['transactions'])
