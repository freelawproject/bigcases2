from django.db import models

from bc.core.models import AbstractDateTimeModel

from .utils.courtlistener import map_cl_to_pacer_id

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
    cl_slug = models.SlugField(
        help_text="URL that the document should map to (the slug)",
        max_length=75,
        blank=True,
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

    @property
    def name_with_summary(self) -> str:
        if self.case_summary:
            return f"{self.docket_name} ({self.case_summary})"
        return self.docket_name

    @property
    def pacer_court_id(self) -> str:
        return map_cl_to_pacer_id(self.cl_court_id)

    @property
    def cl_url(self) -> str:
        return f"https://www.courtlistener.com/recap/gov.uscourts.{self.cl_court_id}.{self.pacer_case_id}"

    def pacer_district_url(self, path) -> str | None:
        if not self.pacer_case_id or self.cl_court_id in APPELLATE_COURT_IDS:
            return None
        return f"https://ecf.{self.pacer_court_id}.uscourts.gov/cgi-bin/{path}?{self.pacer_case_id}"

    def pacer_docket_url(self) -> str | None:
        if not self.pacer_case_id:
            return None

        if self.cl_court_id in APPELLATE_COURT_IDS:
            if self.cl_court_id in ["ca5", "ca7", "ca11"]:
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

    def __str__(self) -> str:
        if self.docket_name:
            return f"{self.pk}: {self.name_with_summary}"
        else:
            return f"{self.pk}"


class FilingWebhookEvent(AbstractDateTimeModel):
    SCHEDULED = 1
    SUCCESSFUL = 2
    FAILED = 3
    IN_PROGRESS = 4
    IGNORED = 5
    WAITING_FOR_DOCUMENT = 6
    CHOICES = (
        (SCHEDULED, "Awaiting processing in queue."),
        (SUCCESSFUL, "Item processed successfully."),
        (FAILED, "Item encountered an error while processing."),
        (IN_PROGRESS, "Item is currently being processed."),
        (IGNORED, "Item ignored"),
        (WAITING_FOR_DOCUMENT, "Awaiting for document purchase"),
    )

    docket_id = models.IntegerField(
        help_text="The docket id from CL.",
        null=True,
    )
    doc_id = models.IntegerField(
        help_text="The document id from CL.",
        null=True,
    )
    pacer_doc_id = models.CharField(
        help_text="The ID of the document in PACER.",
        max_length=32,
        blank=True,
    )
    document_number = models.BigIntegerField(
        help_text="The docket entry number for the document.",
        blank=True,
        null=True,
    )
    long_description = models.TextField(
        help_text="The docket entry's description",
        blank=True,
    )
    short_description = models.TextField(
        help_text="The document description",
        blank=True,
    )
    attachment_number = models.SmallIntegerField(
        help_text=(
            "If the file is an attachment, the number is the attachment "
            "number on the docket."
        ),
        blank=True,
        null=True,
    )
    status = models.SmallIntegerField(
        help_text="The current status of this upload. Possible values "
        "are: %s" % ", ".join([f"({t[0]}): {t[1]}" for t in CHOICES]),
        default=SCHEDULED,
        choices=CHOICES,
    )

    # Post process fields
    subscription = models.ForeignKey(
        Subscription,
        help_text="The subscription that was updated by this request.",
        null=True,
        on_delete=models.SET_NULL,
    )
    post = models.ManyToManyField(
        "channel.Channel",
        help_text="The posts generated after the event is handled",
        related_name="filing_webhook_events",
        through="channel.Post",
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["docket_id"]),
            models.Index(fields=["pacer_doc_id"]),
        ]

    @property
    def cl_document_url(self) -> str | None:
        if not self.subscription:
            return None
        if not self.attachment_number:
            return (
                f"https://www.courtlistener.com/docket/"
                f"{self.docket_id}/"
                f"{self.document_number}/"
                f"{self.subscription.cl_slug}/"
            )
        else:
            return (
                f"https://www.courtlistener.com/docket/"
                f"{self.docket_id}/"
                f"{self.document_number}/"
                f"{self.attachment_number}/"
                f"{self.subscription.cl_slug}/"
            )

    @property
    def description(self) -> str:
        if self.short_description:
            return self.short_description
        return self.long_description

    @property
    def cl_pdf_or_pacer_url(self) -> str:
        return f"{self.cl_document_url}?redirect_or_modal=True"

    @property
    def cl_docket_url(self) -> str | None:
        if not self.subscription:
            return None
        return self.subscription.cl_url

    def __str__(self) -> str:
        description = f"Doc {self.document_number}"
        if self.attachment_number:
            description += f"-{self.attachment_number}"

        if self.subscription:
            description += f" from {self.subscription.docket_name}"

        return description
