"""
SQLAlchemy ORM models
"""

# https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/#configure-the-extension

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa

db = SQLAlchemy()


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    court = db.Column(db.String(100), nullable=False)
    case_number = db.Column(db.String(100), nullable=False)
    bcb1_description = db.Column(db.String(200))
    cl_case_title = db.Column(db.Text)
    cl_docket_id = db.Column(db.Integer)
    in_bcb1 = db.Column(db.Boolean, default=False)
    docket_entries = db.relationship("DocketEntry", back_populates="case")
    documents = db.relationship("Document", back_populates="case")


class DocketEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cl_docket_entry_id = db.Column(db.Integer)
    entry_number = db.Column(
        db.Integer
    )  # See https://www.courtlistener.com/api/rest-info/#docket-entry-endpoint
    pacer_sequence_number = db.Column(db.Integer)
    case_id = db.Column(
        db.Integer, sa.ForeignKey("case.id", ondelete="CASCADE")
    )
    case = db.relationship("Case", back_populates="docket_entries")
    documents = db.relationship("Document", back_populates="docket_entry")


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    docket_entry_id = db.Column(
        db.Integer, sa.ForeignKey("docket_entry.id", ondelete="CASCADE")
    )
    docket_entry = db.relationship("DocketEntry", back_populates="documents")
    case_id = db.Column(
        db.Integer, sa.ForeignKey("case.id", ondelete="CASCADE")
    )
    case = db.relationship("Case", back_populates="documents")
    attachment_number = db.Column(db.Integer)
    document_thumbnails = db.relationship(
        "DocumentThumbnail", back_populates="document"
    )


class DocumentThumbnail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer, sa.ForeignKey("document.id", ondelete="CASCADE")
    )
    page_number = db.Column(db.Integer, nullable=False)
    storage_url = db.Column(db.String(200), nullable=False)  # URL to file on CL storage
    document = db.relationship(
        "Document", back_populates="document_thumbnails"
    )


class Beat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: Friendly name
    # <-> Cases
    # <-> Curators (Users)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    affiliation = db.Column(db.Text)
    # <-> Channels
    # <-> Beats

    # Overall enable switch. Disable to shut out account entirely.
    # Disabled by default; must enable manually
    enabled = db.Column(db.Boolean, default=False)

    # Whether to allow login to Flask app
    # Disabled by default; must enable manually
    allow_login = db.Column(db.Boolean, default=False)

    # Whether to allow spending $$$!
    # Disabled by default; must enable manually
    allow_spend = db.Column(db.Boolean, default=False)

    # Whether to allow commanding BCB to follow a case
    # (passively unless allow_spend is also set)
    # Disabled by default; must enable manually
    allow_follow = db.Column(db.Boolean, default=False)

    # Login stuff
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.Text, nullable=False)


class RegistrationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), nullable=False)
    user_id = db.Column(
        db.Integer, sa.ForeignKey("user.id", ondelete="CASCADE")
    )  # FK to User: set after use
    enabled = db.Column(
        db.Boolean, default=False
    )  # Disabled by default; must enable manually
    used = db.Column(
        db.Boolean, default=False
    )  # Whether this token has been used (they're single-use)

    # TODO: issued_at timestamp
    # TODO: issued_by FK to User
    # TODO: used_at timestamp


class Channel(db.Model):
    """
    A "Channel" is a particular account on a service, which is used by
    BCB to broadcast or to issue commands to BCB.
    """

    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(100), nullable=False)  # e.g., "twitter", "mastodon"
    account = db.Column(db.String(100))  # e.g., "big_cases"
    account_id = db.Column(
        db.String(100), default=None
    )  # Service's ID number for the account, if applicable
    user_id = db.Column(
        db.Integer, sa.ForeignKey("user.id", ondelete="CASCADE")
    )  # FK to User
    enabled = db.Column(
        db.Boolean, default=False
    )  # Disabled by default; must enable manually


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    docket_entry_id = db.Column(
        db.Integer, sa.ForeignKey("docket_entry.id", ondelete="CASCADE")
    )
    case_id = db.Column(
        db.Integer, sa.ForeignKey("case.id", ondelete="CASCADE")
    )
    channel_id = db.Column(
        db.Integer, sa.ForeignKey("channel.id", ondelete="CASCADE")
    )
    channel_post_id = db.Column(db.Text)
    text = db.Column(db.Text)

    # TODO: posted_at TIMESTAMP WITHOUT TIME ZONE


# Many-to-many relationships:
# - Case <-> Beat
# - User <-> Beat
# - Channel <-> Beat
# - Channel <-> User
#     A User's channels should be known so we know whether
#     to accept their commands
