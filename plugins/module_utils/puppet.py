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
            'enable': '--enable',
            'evaltrace': '--evaltrace',
            'fingerprint': '--fingerprint',
            'no_daemonize': '--no-daemonize',
            'no_op': '--noop',
            'onetime': '--onetime',
            'test': '-t',
            'trace': '--trace',
            'verbose': '-v',
        },
        'apply': {
            'debug': '-d',
            'detailed_exitcodes': '--detailed-exitcodes',
            'loadclasses': '-L',
            'no_op': '--noop',
            'test': '-t',
            'verbose': '-v',
            'write_catalog_summary': '--write-catalog-summary',
        },
    }
)

# dictionary that maps input args to puppet args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'agent': {
            'certname': '--certname',
            'digest': '--digest',
            'disable': '--disable',
            'job_id': '--job-id',
            'logdest': '--logdest',
            'server_port': '--serverport',
            'sourceaddress': '--sourceaddress',
            'waitforcert': '--waitforcert',
        },
        'apply': {
            'catalog': '--catalog',
            'execute': '-e',
            'logdest': '-l',
        },
    }
)


def cmd(
    action: str,
    flags: set[str] = set(),
    args: dict[str, str | int] = {},
    manifest: Path = None,
    catalog: Path = None,
    execute: str = None,
) -> list[str]:
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
            # server port arg requires int-->str and validation
            if arg == 'server_port':
                # validate server_port range
                if arg_value < 1 or arg_value > 65535:
                    raise ValueError(f'Puppet server_port value must be between 1 and 65535: {arg_value}')
                arg_value = f'{arg_value}'
            # waitforcert arg requires int-->str
            elif arg == 'waitforcert':
                arg_value = f'{arg_value}'

            # append the value interpolated with the arg name from the dict to the command
            command.extend([action_args_map[arg], arg_value])
        else:
            # unsupported arg specified
            warnings.warn(f'Unsupported Puppet arg specified: {arg}', RuntimeWarning)

    # return the command with the manifest appended if the action is 'apply'
    if action == 'apply':
        # handle execute option
        if execute:
            command.extend(['-e', execute])
        # handle catalog option
        elif catalog:
            # validate catalog file exists
            if Path(catalog).is_file() and universal.validate_json_yaml_file(catalog):
                command.extend(['--catalog', str(catalog)])
            # otherwise error if it does not exist
            else:
                raise FileNotFoundError(f'Puppet catalog file does not exist or is invalid: {catalog}')
        # handle manifest option
        elif manifest:
            # validate manifest file exists
            if Path(manifest).is_file():
                command.extend([str(manifest)])

            # otherwise error if it does not exist
            else:
                raise FileNotFoundError(f'Puppet manifest is not a file or does not exist: {manifest}')
        # one of these options must be provided (typically caught before this point)
        else:
            raise RuntimeError('One of manifest, execute, or catalog must be provided for apply action')

    return command
