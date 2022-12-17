from flask import current_app, render_template, Blueprint
from courts_db import find_court_by_id
from judge_pics.search import portrait, ImageSizes

from .models import db, Case

bp = Blueprint("pages", __name__)


@bp.route("/case/<int:case_id>")
def case_page(case_id):
    the_case: Case = db.session.get(Case, case_id)

    court_name = None
    court_results = find_court_by_id(the_case.court)
    if len(court_results) == 1:
        court_name = court_results[0]["name"]

    return render_template(
        "case.html",
        case_name=the_case.cl_case_title,
        court_name=court_name,
        in_bcb1=the_case.in_bcb1,
        bcb1_desc=the_case.bcb1_description,
        court_id=the_case.court,
        cl_id=the_case.cl_docket_id,
        cl_url=the_case.cl_url(),
        judges=the_case.judges,
        next_id=the_case.id + 1,
    )


# def init_app(app):
#     # https://flask.palletsprojects.com/en/2.2.x/tutorial/database/#register-with-the-application
#     # app.cli.add_command(create_registration_token)
#     pass
