import click
from flask import current_app, Blueprint
from itsdangerous.url_safe import URLSafeSerializer

from bigcases2.models import RegistrationToken, User, db
from bigcases2.misc import generate_key

REG_TOKEN_SALT = "mmmSalty!"

bp = Blueprint("registration", __name__)


@click.command("reg-token")
def create_registration_token(email: str = None, issuer: User = None):
    """
    Create a registration token
    """

    # Generate a new random token
    secret = current_app.config.get("SECRET_KEY")
    clear_token = generate_key(length=16)  # Shorter should be OK here.
    serializer = URLSafeSerializer(secret, salt=REG_TOKEN_SALT)
    url_safe_token = serializer.dumps(clear_token)
    current_app.logger.debug(f"Token: {url_safe_token}")

    new_token = RegistrationToken(
        token=url_safe_token,
        user_id=None,
        enabled=True,
        used=False,
        # TODO: issued_at timestamp
        # TODO: issued_by FK to User
        # TODO: used_at timestamp
    )

    db.session.add(new_token)
    db.session.commit()

    msg = f"Created registration token #{new_token.id}: {url_safe_token}"
    current_app.logger.info(msg)
    click.echo(msg)

    # TODO: Send an email to the target; cc issuer if present
    if email is not None:
        pass


def init_app(app):
    # https://flask.palletsprojects.com/en/2.2.x/tutorial/database/#register-with-the-application
    app.cli.add_command(create_registration_token)
