"""RCON client CLI."""

from argparse import ArgumentParser
from logging import DEBUG, INFO, basicConfig, getLogger
from subprocess import CalledProcessError, check_call
from sys import exit    # pylint: disable=W0622

from mcipc.cli.common import get_creadentials
from mcipc.config import LOG_FORMAT
from mcipc.rcon.playground import Client


__all__ = ['get_args', 'run_action', 'main']


LOGGER = getLogger('rconclt')


def get_args():
    """Parses and returns the CLI arguments."""

    parser = ArgumentParser(description='A Minecraft RCON client.')
    parser.add_argument('server', help="the server's name")
    subparsers = parser.add_subparsers(dest='action')
    command_parser = subparsers.add_parser(
        'exec', help='execute commands on the server')
    command_parser.add_argument(
        'command', help='command to execute on the server')
    command_parser.add_argument(
        'argument', nargs='*', default=(), help='arguments for the command')
    say_parser = subparsers.add_parser(
        'say', help='broadcast a message on the server')
    say_parser.add_argument('message', help='the message to broadcast')
    fortune_parser = subparsers.add_parser(
        'fortune', help='send a fortune to the players on the server')
    fortune_parser.add_argument(
        '-l', '--long', action='store_true', help='generate ling fortunes')
    fortune_parser.add_argument(
        '-o', '--offensive', action='store_true',
        help='generate offensive fortunes')
    datetime_parser = subparsers.add_parser(
        'datetime',
        help='sends the current date and time to the players on the server')
    datetime_parser.add_argument(
        '-f', '--format', default='%c', help='the datetime format')
    subparsers.add_parser('in-use', help='checks whether the server is in use')
    shutdown_parser = subparsers.add_parser(
        'idle-shutdown', help='shuts down the server if it is not in use')
    shutdown_parser.add_argument(
        '-s', '--sudo', action='store_true',
        help='invoke the shutdown command using sudo')
    shutdown_parser.add_argument(
        '-u', '--unit', default='minecraft@{server}.service',
        help='the systemd unit template')
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='print additional debug information')
    return parser.parse_args()


def idle_shutdown(players, args):
    """Shuts down the server if it is idle."""

    if players.online:
        LOGGER.info('Server is in use.')
        return False

    LOGGER.info('Server is idle.')
    unit = args.unit.format(server=args.server)
    command = ('/usr/bin/systemctl', 'stop', unit)

    try:
        check_call(command)
    except CalledProcessError as error:
        LOGGER.error('Could not shutdown the server.')
        LOGGER.debug(error)
        return False

    LOGGER.info('Server %s has been shut down.', unit)
    return True


def run_action(client, args):
    """Runs the respective actions."""

    result = None

    if args.action == 'exec':
        result = client.run(args.command, *args.argument)
    elif args.action == 'say':
        result = client.say(args.message)
    elif args.action == 'fortune':
        result = client.fortune(
            short=not args.long, offensive=args.offensive)
    elif args.action == 'datetime':
        result = client.datetime(frmt=args.format)
    elif args.action == 'in-use':
        players = client.players

        if players.online:
            LOGGER.info('There are %i players online:', players.online)
            LOGGER.info(', '.join(players.names))
        else:
            LOGGER.warning('There are no players online.')
            exit(1)

    if result:
        LOGGER.info(result)


def main():
    """Runs the RCON client."""

    args = get_args()
    log_level = DEBUG if args.debug else INFO
    basicConfig(level=log_level, format=LOG_FORMAT)
    host, port, passwd = get_creadentials(args.server, logger=LOGGER)

    with Client(host, port) as client:
        if not client.login(passwd):
            LOGGER.error('Failed to log in.')
            exit(4)

        if args.action == 'idle-shutdown':
            players = client.players
        else:
            run_action(client, args)

    if args.action == 'idle-shutdown':
        if not idle_shutdown(players, args):
            exit(1)
