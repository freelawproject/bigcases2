from django.db import models

from bc.core.models import AbstractDateTimeModel

APPELLATE_COURT_IDS = [
    "ca1",
    "ca2",
    "ca3",
    "ca4",
    "ca5",
    "ca6",
    "ca7",
    "ca8",
    "ca9",
    "ca10",
    "ca11",
    "cadc",
    "cafc",
]


class Subscription(AbstractDateTimeModel):
    docket_name = models.TextField(
        help_text="The name of the docket",
    )
    docket_number = models.CharField(
        help_text="The docket numbers of a case",
        max_length=100,
        blank=True,
    )
    court_name = models.CharField(
        help_text="The court where the upload was from",
        max_length=100,
    )
    case_summary = models.CharField(
        help_text="A few words to describe the case in social media",
        max_length=100,
        blank=True,
    )
    cl_docket_id = models.IntegerField(
        help_text="The docket id from CourtListener db.",
        null=True,
    )
    cl_court_id = models.CharField(
        help_text="The CL court ID, b/c it's sometimes different from PACER's",
        max_length=100,
    )
    pacer_court_id = models.CharField(
        help_text="The ID in PACER's subdomain",
        max_length=10,
    )
    pacer_case_id = models.CharField(
        help_text=(
            "The cased ID provided by PACER. Noted in this case on a "
            "per-document-level, since we've learned that some "
            "documents from other cases can appear in curious places."
        ),
        max_length=100,
        blank=True,
    )

    def cl_url(self):
        return f"https://www.courtlistener.com/recap/gov.uscourts.{self.cl_court_id}.{self.pacer_case_id}"

    def pacer_district_url(self, path):
        if not self.pacer_case_id or self.cl_court_id in APPELLATE_COURT_IDS:
            return None
        return f"https://ecf.{self.pacer_court_id}.uscourts.gov/cgi-bin/{path}?{self.pacer_case_id}"

    def pacer_docket_url(self):
        if not self.pacer_case_id:
            return None

        if self.cl_court_id in APPELLATE_COURT_IDS:
            if self.court.pk in ["ca5", "ca7", "ca11"]:
                path = "/cmecf/servlet/TransportRoom?"
            else:
                path = "/n/beam/servlet/TransportRoom?"

            return (
                f"https://ecf.{self.pacer_court_id}.uscourts.gov"
                f"{path}"
                f"servlet=CaseSummary.jsp&"
                f"caseId={self.pacer_case_id}&"
                f"incOrigDkt=Y&"
                f"incDktEntries=Y"
            )
        else:
            return self.pacer_district_url("DktRpt.pl")
