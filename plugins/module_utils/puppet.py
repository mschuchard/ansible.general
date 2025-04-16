"""puppet agent module utilities"""

__metaclass__ = type

import warnings
from typing import Final
from pathlib import Path
from mschuchard.general.plugins.module_utils import universal


# dictionary that maps input args to puppet flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'agent': {
            'debug': '-d',
            'no_daemonize': '--no-daemonize',
            'no_op': '--noop',
            'onetime': '--onetime',
            'test': '-t',
            'verbose': '-v',
        },
        'apply': {
            'debug': '-d',
            'no_op': '--noop',
            'test': '-t',
            'verbose': '-v',
        },
    }
)

# dictionary that maps input args to puppet args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'agent': {
            'certname': '--certname',
            'server_port': '--serverport',
        },
    }
)


def cmd(action: str, flags: set[str] = [], args: dict[str, str] = {}, manifest: Path = Path.cwd()) -> list[str]:
    """constructs a list representing the puppet command to execute"""
    # verify command
    if action not in FLAGS_MAP:
        raise RuntimeError(f'Unsupported Puppet action attempted: {action}')

    # initialize puppet command
    command: list[str] = ['puppet', action]

    # append list of flag commands
    universal.action_flags_command(command, flags, FLAGS_MAP.get(action, {}))

    # construct list of puppet args
    action_args_map: dict = ARGS_MAP.get(action, {})
    for arg, arg_value in args.items():
        # verify this is a valid action argument
        if arg in action_args_map:
            # server port arg requires int-->str
            if arg == 'server_port':
                arg_value = f'{arg_value}'

            # append the value interpolated with the arg name from the dict to the command
            command.extend([action_args_map[arg], arg_value])
        else:
            # unsupported arg specified
            warnings.warn(f'Unsupported Puppet arg specified: {arg}', RuntimeWarning)

    # return the command with the manifest appended if the action is 'apply'
    if action == 'apply':
        if Path(manifest).is_file():
            return command + [str(manifest)]

        # otherwise error if it does not exist
        raise FileNotFoundError(f'Puppet manifest is not a file or does not exist: {manifest}')

    return command
