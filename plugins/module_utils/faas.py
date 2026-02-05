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
            'squash': '--squash',
        },
        'deploy': {
            'replace': '--replace',
            'update': '--update=false',
        },
        'list': {'verbose': '-v'},
        'logs': {
            'instance': '--instance',
        },
        'push': {'env_subst': '--envsubst=false'},
    }
)

# dictionary that maps input args to terraform args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'build': {
            'build_arg': '',
            'build_label': '',
            'build_option': '',
            'copy_extra': '',
            'handler': '--handler',
            'image': '--image',
            'lang': '--lang',
            'name': '--name',
            'parallel': '--parallel',
            'tag': '--tag',
        },
        'deploy': {
            'annotation': '',
            'label': '',
            'name': '--name',
        },
        'list': {'sort': '--sort'},
        'logs': {'name': ''},
        'login': {
            'username': '-u',
            'password': '-p',
        },
        'push': {
            'parallel': '--parallel',
            'tag': '--tag',
        },
        'remove': {'name': ''},
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
            # annotation, label, build_arg, build_label, build_option, and copy_extra have properly formatted value of type list[str] and so need to be extended directly
            if arg in ['annotation', 'label', 'build_arg', 'build_label', 'build_option', 'copy_extra']:
                command.extend(arg_value)
            # name arg is actually positional for logs and remove, and so just append the value
            elif action in ['logs', 'remove'] and arg == 'name':
                command.append(arg_value)
            # convert parallel argument from int-->str
            elif arg == 'parallel':
                command.extend([action_args_map[arg], f'{arg_value}'])
            # append the value interpolated with the arg name from the dict to the command
            else:
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


def ansible_to_faas(args: dict) -> None:
    """converts ansible types and syntax to faas types and formatting for arguments only"""
    # in this function args dict is mutable pseudo-reference and also returned
    # iterate through ansible module argument
    for arg, arg_value in args.items():
        match arg:
            # transform dict[str, str] to list of '--arg' 'key=value' '--arg' 'key2=value2' strings
            case 'annotation' | 'label' | 'build_arg' | 'build_label':
                args[arg] = ' '.join([f'--{arg.replace("_", "-")} {key}={value}' for key, value in arg_value.items()]).split()
            # transform list[str] to list of '--build-option' 'value1' '--build-option' 'value2' strings
            case 'build_option':
                args[arg] = ' '.join([f'--build-option {value}' for value in arg_value]).split()
            # transform list[Path] to list of '--copy-extra' 'path1' '--copy-extra' 'path2' strings
            case 'copy_extra':
                args[arg] = ' '.join([f'--copy-extra {str(path)}' for path in arg_value]).split()
