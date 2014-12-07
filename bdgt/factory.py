import logging
from logging.handlers import SMTPHandler

from flask import Flask


_log = logging.getLogger(__name__)


def create_app(settings=None):
    _log.info("Creating app")

    app = Flask(__name__, static_folder='frontend/static',
                template_folder='frontend/templates')
    app.config.from_object('bdgt.default_settings')
    if settings:
        app.config.update(settings)
    else:  # pragma: no cover
        app.config.from_envvar('BDGT_SETTINGS')  # pragma: no cover

    # Ignore Flask's built-in logging
    # app.logger is accessed here so Flask tries to create it
    app.logger_name = "nowhere"
    app.logger

    # Configure logging.
    #
    # It is somewhat dubious to get _log from the root package, but I can't see
    # a better way. Having the email handler configured at the root means all
    # child loggers inherit it.
    from bdgt import _log as root_logger

    # Only log to email during production.
    if not app.debug and not app.testing:  # pragma: no cover
        mail_handler = SMTPHandler((app.config["MAIL_SERVER"],
                                   app.config["MAIL_SMTP_PORT"]),
                                   app.config["MAIL_FROM"],
                                   app.config["MAIL_TO"],
                                   "bdgt failed")
        mail_handler.setLevel(logging.ERROR)
        root_logger.addHandler(mail_handler)
        mail_handler.setFormatter(
            logging.Formatter("Message type: %(levelname)s\n" +
                              "Location: %(pathname)s:%(lineno)d\n" +
                              "Module: %(module)s\n" +
                              "Function: %(funcName)s\n" +
                              "Time: %(asctime)s\n" +
                              "Message:\n" +
                              "%(message)s"))

    # Only log to the console during development and production, but not
    # during testing.
    if not app.testing:  # pragma: no cover
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)

    # Only log debug messages during development
    if app.debug:  # pragma: no cover
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)

    # Initialise extensions
    from bdgt import db, toolbar
    db.init_app(app)
    toolbar.init_app(app)

    # Register blueprints
    from bdgt.frontend.accounts.views import bp as accounts_bp
    from bdgt.frontend.categories.views import bp as categories_bp
    from bdgt.frontend.dashboard.views import bp as dashboard_bp
    from bdgt.frontend.imports.views import bp as imports_bp
    from bdgt.frontend.transactions.views import bp as transactions_bp
    app.register_blueprint(accounts_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(imports_bp)
    app.register_blueprint(transactions_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
