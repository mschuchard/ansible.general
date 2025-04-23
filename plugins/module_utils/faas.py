"""faas module utilities"""

__metaclass__ = type


from typing import Final
from pathlib import Path
from mschuchard.general.plugins.module_utils import universal

# dictionary that maps input args to terraform flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'build': {
            'disable_stack_pull': '--disable-stack-pull',
            'env_subst': '--envsubst',
            'no_cache': '--no-cache',
            'pull': '--pull',
            'quiet': '--quiet',
            'shrinkwrap': '--shrinkwrap',
        },
        'deploy': {},
        'invoke': {},
        'list': {},
        'login': {},
        'logs': {},
        'push': {},
        'remove': {},
    }
)

# dictionary that maps input args to terraform args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'build': {},
        'deploy': {},
        'invoke': {},
        'list': {},
        'login': {},
        'logs': {},
        'push': {},
        'remove': {},
    }
)


def cmd(action: str, flags: set[str] = [], args: dict[str, str] = {}, name: str = None) -> list[str]:
    """constructs a list representing the openfaas command to execute"""
    # verify command
    if action not in FLAGS_MAP:
        raise RuntimeError(f'Unsupported FaaS action attempted: {action}')

    # initialize faas-cli command
    command: list[str] = ['faas-cli', action] + global_args_to_cmd(args=args)

    # append list of flag commands
    universal.action_flags_command(command, flags, FLAGS_MAP.get(action, {}))

    return command


def global_args_to_cmd(args: dict = {}) -> list[str]:
    """converts openfaas global arguments into a list of strings suitable for extending to a command"""
    # initialize command to return
    command: list[str] = []

    # check if filter is specified
    if 'filter' in args:
        command.extend(['--filter', args['filter']])

    # check if regex is specified
    if 'regex' in args:
        command.extend('--regex', args['regex'])

    # check if config file is specified
    if 'config_file' in args:
        config_file: Path = Path(args['config_file'])
        # verify faas function config file is a file, and a valid yaml file
        if config_file.is_file() and universal.validate_json_yaml_file(config_file):
            # config file is valid
            command.extend(['-f', str(config_file)])
        else:
            # error if config file has issue
            raise FileNotFoundError(f'Function config file does not exist or is invalid: {config_file}')

    return command
