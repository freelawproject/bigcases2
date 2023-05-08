from prettytable import PrettyTable

from bc.channel.models import Channel, Group


def show_all_channels_table() -> tuple[PrettyTable, dict[int, Channel]]:
    """
    Builds a table to show the list of enabled channels

    Returns:
        tuple[PrettyTable, dict[int,Channel]]: returns the table and a dict with the data as a tuple
    """
    table = PrettyTable()
    mapping = {}
    table.field_names = ["ID", "Service", "Account", "Enabled", "URL", "Group"]
    db_channels = Channel.objects.all()
    for channel in db_channels:
        table.add_row(
            [
                channel.id,
                channel.service,
                channel.account,
                channel.enabled,
                channel.self_url(),
                channel.group,
            ]
        )
        mapping[channel.id] = channel

    return table, mapping


def show_channel_groups_table() -> tuple[PrettyTable, dict[int, Group]]:
    """
    Builds a table to show the list of channel

    Returns:
        tuple[PrettyTable, dict[int,Group]]: returns the table and a dict with the data as a tuple
    """
    table = PrettyTable()
    mapping = {}
    table.field_names = ["ID", "Name", "Channels"]
    db_groups = Group.objects.all()
    for group in db_groups:
        table.add_row(
            [
                group.id,
                group.name,
                ",".join(
                    [
                        f"{ch.get_service_display()}: {ch.account}"
                        for ch in group.channels.all()
                    ]
                ),
            ]
        )
        mapping[group.id] = group

    return table, mapping
