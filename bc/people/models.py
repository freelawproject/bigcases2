from django.db import models
from judge_pics.search import ImageSizes, portrait

from bc.core.models import AbstractDateTimeModel


class Judge(AbstractDateTimeModel):
    cl_person_id = models.IntegerField(
        help_text="The person id from Courtlistener db."
    )
    name_first = models.CharField(
        help_text="The first name of this person.",
        max_length=50,
    )
    name_middle = models.CharField(
        help_text="The middle name or names of this person",
        max_length=50,
        blank=True,
    )
    name_last = models.CharField(
        help_text="The last name of this person",
        max_length=50,
        db_index=True,
    )
    name_suffix = models.CharField(
        help_text="Any suffixes that this person's name may have",
        max_length=200,
    )

    def name(self):
        n = ""
        if self.name_middle and self.name_middle != "":
            n = f"{self.name_first} {self.name_middle} {self.name_last}"
        else:
            n = f"{self.name_first} {self.name_last}"
        if self.name_suffix and self.name_suffix != "":
            n = f"{n}, {self.name_suffix}"
        return n

    def portrait(self, size: ImageSizes = ImageSizes.SMALL):
        portrait_url = portrait(self.cl_person_id, size)
        return portrait_url

    @staticmethod
    def from_json(json_data):
        existing = Judge.objects.filter(cl_person_id=json_data["id"]).first()

        if existing:
            return existing

        else:
            j = Judge.objects.create(
                cl_person_id=json_data["id"],
                name_first=json_data["name_first"],
                name_middle=json_data["name_middle"],
                name_last=json_data["name_last"],
                name_suffix=json_data["name_suffix"],
            )
            return j
