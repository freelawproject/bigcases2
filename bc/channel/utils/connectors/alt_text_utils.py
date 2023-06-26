# Connector utilities for creating alt-text


def thumb_num_alt_text(thumbnail_number: int = 0) -> str:
    """
    The alt-text for a thumbnail of a PDF. If the thumbnail is one of a
    list of thumbnails, then pass in the zero-based index number of the
    thumbnail in the list.

    Args:
        thumbnail_number (int): the index number of the thumbnail in a list
        of thumbnails.
        Default is 0,

    Returns:
        (str)
    """
    return f"Thumbnail of page {thumbnail_number + 1} of the PDF linked above."


def text_image_alt_text(text_image_description: str = "") -> str:
    """
    The alt-text for an image description.

    Args:
        text_image_description (str):

    Returns:
        (str)
    """
    return f"An image of the entry's full text: {text_image_description}"
