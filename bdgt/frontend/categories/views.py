import logging

from flask import Blueprint, redirect, render_template, url_for


from bdgt import db
from bdgt.domain.models import Category
from bdgt.frontend.categories.forms import CategoryForm


_log = logging.getLogger(__name__)

bp = Blueprint('categories', __name__, url_prefix="/category")


@bp.route("/", methods=['GET'])
def index():
    root_categories = Category.query.filter_by(parent_id=None).all()
    return render_template("categories/index.html", categories=root_categories)


@bp.route("/new", methods=['GET', 'POST'])
@bp.route("/edit/<int:id>", methods=['GET', 'POST'])
def create_or_update(id=None):
    if id is None:
        title = "Add Category"
        category = Category()
    else:
        title = "Edit Category"
        category = Category.query.get(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        form.populate_obj(category)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('categories.index'))
    return render_template('form.html', form=form, form_title=title,
                           action_url=url_for('categories.create_or_update',
                                              id=id))


@bp.route("/delete/<int:id>")
def delete(id):
    category = Category.query.get(id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('categories.index'))
