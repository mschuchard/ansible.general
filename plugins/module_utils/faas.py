"""faas module utilities"""

__metaclass__ = type

import warnings
from typing import Final
from pathlib import Path
from mschuchard.general.plugins.module_utils import universal

# dictionary that maps input args to terraform flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'build': {
            'disable_stack_pull': '--disable-stack-pull',
            'env_subst': '--envsubst=false',
            'no_cache': '--no-cache',
            'pull': '--pull',
            'quiet': '--quiet',
            'shrinkwrap': '--shrinkwrap',
        },
        'deploy': {
            'replace': '--replace',
            'update': '--update=false',
        },
        'list': {'verbose': '-v'},
        'logs': {
            'instance': '--instance',
            'name': '--name',
        },
    }
)

# dictionary that maps input args to terraform args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'build': {'name': '--name'},
        'deploy': {
            'annotation': '',
            'label': '',
            'name': '--name',
        },
        'list': {'sort': '--sort'},
        'login': {
            'username': '-u',
            'password': '-p',
        },
        'push': {'parellel': '--parallel'},
        'remove': {},
    }
)


def cmd(action: str, flags: set[str] = set(), args: dict[str, str] = {}) -> list[str]:
    """constructs a list representing the openfaas command to execute"""
    # verify command
    if action not in FLAGS_MAP | ARGS_MAP:
        raise RuntimeError(f'Unsupported FaaS action attempted: {action}')

    # initialize faas-cli command
    command: list[str] = ['faas-cli', action] + global_args_to_cmd(args=args)

    # append list of flag commands
    universal.action_flags_command(command, flags, FLAGS_MAP.get(action, {}))

    # construct list of faas args
    # not all actions have args, so return empty dict by default to shortcut to RuntimeError for unsupported arg if arg specified for action without args
    action_args_map: dict = ARGS_MAP.get(action, {})
    for arg, arg_value in args.items():
        # verify this is a valid action argument
        if arg in action_args_map:
            if arg == 'sort' and arg_value not in ['name', 'invocations']:
                raise ValueError('The "sort" parameter must be either "name" or "invocations"')

            # append the value interpolated with the arg name from the dict to the command
            command.extend([action_args_map[arg], arg_value])
        else:
            # unsupported arg specified
            warnings.warn(f'Unsupported FaaS arg specified: {arg}', RuntimeWarning)

    return command


def global_args_to_cmd(args: dict = {}) -> list[str]:
    """converts openfaas global arguments into a list of strings suitable for extending to a command"""
    # initialize command to return
    command: list[str] = []

    # check if filter is specified
    if 'filter' in args:
        command.extend(['--filter', args['filter']])
        del args['filter']

    # check if regex is specified
    if 'regex' in args:
        command.extend(['--regex', args['regex']])
        del args['regex']

    # check if config file is specified
    if 'config_file' in args:
        config_file: Path = Path(args['config_file'])
        # verify faas function config file is a file, and a valid yaml file
        if config_file.is_file() and universal.validate_json_yaml_file(config_file):
            # config file is valid
            command.extend(['-f', str(config_file)])
            del args['config_file']
        else:
            # error if config file has issue
            raise FileNotFoundError(f'Function config file does not exist or is invalid: {config_file}')

    return command


def ansible_to_faas(args: dict) -> dict[str, str]:
    """converts ansible types and syntax to faas types and formatting for arguments only"""
    # in this function args dict is mutable pseudo-reference and also returned
    # iterate through ansible module argument
    for arg, arg_value in args.items():
        match arg:
            # transform dict[str, str] to single "key=value key2=value2" string
            case 'annotation' | 'label':
                args[arg] = ' '.join([f'{key}={value}' for key, value in arg_value.items()])

    return args
