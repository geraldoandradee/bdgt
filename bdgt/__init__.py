import logging

from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy


_VERSION = '0.0.0'


# Create the top-level logger. This is required because Flask's built-in method
# results in loggers with the incorrect level.
_log = logging.getLogger(__name__)

db = SQLAlchemy()
toolbar = DebugToolbarExtension()


def get_version():
    return _VERSION
