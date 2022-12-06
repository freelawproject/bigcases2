# https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/#configure-the-extension

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    court = db.Column(db.String(100))
    case_number = db.Column(db.String(100))
    bcb1_description = db.Column(db.String(200))
    cl_case_title = db.Column(db.Text)
    cl_docket_id = db.Column(db.Integer)
    in_bcb1 = db.Column(db.Boolean, default=False)
