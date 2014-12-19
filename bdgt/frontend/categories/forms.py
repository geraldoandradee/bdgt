from flask_wtf import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.orm import model_form

from bdgt.domain.models import Category


CategoryFormBase = model_form(Category, base_class=Form,
                              exclude=['parent', 'parent_id', 'subcategories',
                                       'transactions'])


class CategoryForm(CategoryFormBase):
    parent = QuerySelectField(query_factory=lambda: Category.query.all(),
                              allow_blank=True)
