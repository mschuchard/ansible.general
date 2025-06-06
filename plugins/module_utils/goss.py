"""goss module utilities"""

__metaclass__ = type

import json
import warnings
from typing import Final
from pathlib import Path
from mschuchard.general.plugins.module_utils import universal


# dictionary that maps input args to goss flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'render': {'debug': '--debug'},
    }
)

# dictionary that maps input args to goss args
GLOBAL_ARGS_MAP: Final[dict[str, str]] = dict({'package': '--package', 'vars': '--vars', 'vars_inline': '--vars-inline'})
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'serve': {
            'cache': '-c',
            'endpoint': '-e',
            'format': '-f',
            'format_opts': '-o',
            'max_concur': '--max-concurrent',
            'port': '-l',
        },
        'validate': {
            'format': '-f',
            'format_opts': '-o',
            'max_concur': '--max-concurrent',
            'retry_timeout': '-r',
            'sleep': '-s',
        },
    }
)


def cmd(action: str, flags: set[str] = set(), args: dict[str, str | int | dict] = {}, gossfile: Path = Path.cwd()) -> list[str]:
    """constructs a list representing the goss command to execute"""
    # verify command
    if action not in FLAGS_MAP | ARGS_MAP:
        raise RuntimeError(f'Unsupported GoSS action attempted: {action}')

    # initialize goss command with executable, global args, and action
    # IMPORTANT: global_args_to_cmd mutates the args reference by removing global argument entries
    command: list[str] = ['goss'] + global_args_to_cmd(args=args, gossfile=gossfile) + [action]

    # disable color if validate action
    if action == 'validate':
        command.append('--no-color')

    # append list of flag commands
    universal.action_flags_command(command, flags, FLAGS_MAP.get(action, {}))

    # construct list of goss args
    # not all actions have args, so return empty dict by default to shortcut to RuntimeError for unsupported arg if arg specified for action without args
    action_args_map: dict = ARGS_MAP.get(action, {})
    for arg, arg_value in args.items():
        # verify this is a valid action argument
        if arg in action_args_map:
            # port arg requires int-->str and : prefix
            if arg == 'port':
                arg_value = f':{arg_value}'
            elif arg == 'format' and arg_value not in [
                'documentation',
                'json',
                'json_oneline',
                'junit',
                'nagios',
                'prometheus',
                'rspecish',
                'silent',
                'structured',
                'tap',
            ]:
                raise ValueError('The "format" parameter value must be a valid accepted format for GoSS')
            elif arg == 'format_opts' and arg_value not in ['perfdata', 'pretty', 'verbose']:
                raise ValueError('The "format_opts" parameter value must be one of: perfdata, pretty, or verbose.')

            # append the value interpolated with the arg name from the dict to the command
            command.extend([action_args_map[arg], arg_value])
        else:
            # unsupported arg specified
            warnings.warn(f'Unsupported GoSS arg specified: {arg}', RuntimeWarning)

    return command


def global_args_to_cmd(args: dict = {}, gossfile: Path = Path.cwd()) -> list[str]:
    """converts goss global arguments into a list of strings suitable for extending to a command"""
    # initialize command to return
    command: list[str] = []

    # check if vars is specified
    if 'vars' in args:
        vars_file: Path = args['vars']
        # verify vars file exists
        if Path(vars_file).is_file() and universal.validate_json_yaml_file(Path(vars_file)):
            command.extend([GLOBAL_ARGS_MAP['vars'], str(vars_file)])
            # remove vars from args to avoid doublecheck with action args
            del args['vars']
        else:
            raise FileNotFoundError(f'Vars file does not exist or is invalid: {args["vars"]}')
    # check if vars_inline is specified (exclusive with vars)
    elif 'vars_inline' in args:
        # validate the conversion of the vars inline param value to a json string and extend command
        vars_inline_values: dict = args['vars_inline']
        try:
            command.extend([GLOBAL_ARGS_MAP['vars_inline'], json.dumps(vars_inline_values)])
        except TypeError as exc:
            warnings.warn(f'The vars_inline parameter values {vars_inline_values} could not be encoded to a JSON format string', SyntaxWarning)
            raise TypeError(exc) from exc
        # remove vars_inline from args to avoid doublecheck with action args
        del args['vars_inline']

    # check if package is specified
    if 'package' in args:
        # validate package argument
        package_type: str = args['package']
        if package_type not in ['apk', 'dpkg', 'pacman', 'rpm']:
            raise ValueError(f'The specified parameter value for package {package_type} is not acceptable for GoSS')
        # extend command
        command.extend([GLOBAL_ARGS_MAP['package'], package_type])
        # remove package from args to avoid doublecheck with action args
        del args['package']

    # check if gossfile is default so we use implicit cwd within goss cli instead of module logic
    if gossfile != Path.cwd():
        # verify gossfile is a file, and a valid json or yaml file
        if Path(gossfile).is_file() and universal.validate_json_yaml_file(Path(gossfile)):
            # the gossfile argument is universal and must be immediately specified before action
            command.extend(['-g', str(gossfile)])
        else:
            # error if gossfile does not exist
            raise FileNotFoundError(f'GoSSfile does not exist or is invalid: {gossfile}')

    return command
