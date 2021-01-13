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
