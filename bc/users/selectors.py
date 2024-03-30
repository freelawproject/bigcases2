from django.db.models import QuerySet

from .models import User


def get_curators_by_channel_group_id(channel_group_id: int) -> QuerySet[User]:
    """Queries all curators associated with a given channel group.

    Args:
        channel_group_id (int): The ID of the channel group to query curators.

    Returns:
        QuerySet[User]: QuerySet of User objects representing the curators of
        the channels within the group.
    """
    return User.objects.filter(channels__group_id=channel_group_id).distinct(
        "id"
    )
