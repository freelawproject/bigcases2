"""
bigcases2 app setup
"""

import os

import toml
from flask import Flask


def create_app(test_config=None):
    """
    Create and configure the app.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.logger.debug("__init__.create_app() called")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile("config.py", silent=True)
        TOML_FN = os.path.join(app.instance_path, "config.toml")
        app.logger.debug(f"Loading configuration TOML file: {TOML_FN}")
        app.config.from_file(TOML_FN, load=toml.load)
        app.logger.debug(f"app.config after loading TOML: {app.config}")
        app.logger.debug("-" * 50)
    else:
        # load the test config if passed in
        app.logger.debug(f"Loading test_config: {test_config}")
        app.config.from_mapping(test_config)
        app.logger.debug(f"app.config after adding test_config: {app.config}")
        app.logger.debug("-" * 50)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Database

    # https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/#configure-the-extension
    # app.logger.debug(app.config.get("SQLALCHEMY_DATABASE_URI"))

    from bigcases2.models import db

    db.init_app(app)

    # CourtListener webhook

    from . import courtlistener

    app.register_blueprint(courtlistener.bp)
    courtlistener.init_app(app)

    # Mastodon

    from . import masto

    app.register_blueprint(masto.bp)
    masto.init_app(app)

    # Registration stuff

    from . import registration
    app.register_blueprint(registration.bp)
    registration.init_app(app)

    # CLI

    from . import cli

    cli.init_app(app)

    return app
