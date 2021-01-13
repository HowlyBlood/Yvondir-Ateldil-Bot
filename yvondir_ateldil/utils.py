import re


def extract_command_args(command):
    """
    For example:
    /set_date nSS 2020-10-11 14:30
    => ['nSS', '2020-10-11', '14:30']

    :param command: bot command with arguments
    :return: List containing command stripped from header
    """
    return re.match(r'^(?:/\w+)\s(.*)$', command).group(1).split()


def find_raid_from_message(raid_list, message_id):
    for raid in raid_list.values():
        if raid.discord_message_identifier == message_id:
            return raid
    return None
