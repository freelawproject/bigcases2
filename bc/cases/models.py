from django.db import models

from bc.core.models import AbstractDateTimeModel
from bc.people.models import Judge


class Docket(AbstractDateTimeModel):
    court = models.CharField(
        help_text="The court where the upload was from",
        max_length=100,
    )
    docket_number = models.CharField(
        help_text="The docket numbers of a case",
        max_length=100,
    )
    bcb1_description = models.CharField(
        help_text="Name from the list of cases used in the first version",
        max_length=200,
    )
    in_bcb1 = models.BooleanField(
        help_text="Whether a Docket was used in the first version",
        default=False,
    )
    cl_case_title = models.TextField(
        help_text="the highest quality case name."
    )
    cl_docket_id = models.IntegerField(
        help_text="The docket id from Courtlistener db.", null=True
    )
    cl_slug = models.TextField(
        help_text="URL that the document should map to (the slug)."
    )
    cl_alerts = models.BooleanField(
        help_text="Whether a document has alerts turn on.", default=False
    )
    judges = models.ManyToManyField(
        Judge,
        help_text="The judges for the case.",
        related_name="cases",
    )

    def cl_url(self):
        return f"https://www.courtlistener.com/docket/{self.cl_docket_id}/{self.cl_slug}/"


class DocketEntry(AbstractDateTimeModel):
    docket = models.ForeignKey(
        Docket,
        help_text="Foreign key as a relation to the Docket object.",
        related_name="docket_entries",
        on_delete=models.CASCADE,
    )
    cl_docket_entry_id = models.IntegerField(
        help_text="The entry id from Courtlistener db."
    )
    entry_number = models.IntegerField(
        help_text="The docket entry number for the document."
    )
    pacer_sequence_number = models.IntegerField(
        help_text="A field used for ordering the docket entries on a docket."
    )


class Document(AbstractDateTimeModel):
    docket_entry = models.ForeignKey(
        DocketEntry,
        help_text="Foreign Key to the DocketEntry object",
        related_name="documents",
        on_delete=models.CASCADE,
    )
    docket = models.ForeignKey(
        Docket,
        help_text="Foreign Key to the Docket object",
        related_name="documents",
        on_delete=models.CASCADE,
    )
    attachment_number = models.IntegerField(
        help_text=(
            "If the file is an attachment, This field stores the attachment "
            "number in RECAP docket."
        ),
    )


class DocumentThumbnail(AbstractDateTimeModel):
    page_number = models.IntegerField(
        help_text="Page number of the thumbnail."
    )
    thumbnail = models.ImageField(help_text="URL to the file on CL storage.")
    document = models.ForeignKey(
        Document,
        help_text="'Foreign Key to the Document object.",
        related_name="thumbnails",
        on_delete=models.CASCADE,
    )
