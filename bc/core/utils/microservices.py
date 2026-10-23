from io import BytesIO
from zipfile import ZipFile

import requests
from django.conf import settings


def doctor_auth_headers() -> dict[str, str]:
    """
    Returns the bearer token header doctor requires once its own
    DOCTOR_AUTH_TOKENS setting is on, or nothing while DOCTOR_AUTH_TOKEN
    is blank.
    """
    token = settings.DOCTOR_AUTH_TOKEN
    return {"Authorization": f"Bearer {token}"} if token else {}


def get_thumbnails_from_range(document: bytes, page_range: str) -> list[bytes]:
    """
    Returns a list that contains a thumbnail(as a binary object) for each
    page requested.

    Args:
        document (bytes): document content as bytes
        page_range (str): str representation of the list of pages requested

    Returns:
        list[bytes]: list of thumbnails
    """
    thumbnails = requests.post(
        f"{settings.DOCTOR_HOST}/convert/pdf/thumbnails/",
        data={"pages": page_range, "max_dimension": "1920"},
        files={"file": ("dummy.pdf", document)},
        headers=doctor_auth_headers(),
        timeout=60,
    )

    zipfile = ZipFile(BytesIO(thumbnails.content))
    return [
        zipfile.open(file_name).read()
        for file_name in sorted(zipfile.namelist())
    ]
