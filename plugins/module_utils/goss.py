"""goss module utilities"""
__metaclass__ = type

from typing import Final
from pathlib import Path


# dictionary that maps input args to goss flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'render': {'debug': '--debug'},
})

# dictionary that maps input args to goss args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'serve': {
        'endpoint': '-e',
        'format': '-f',
        'port': '-l',
    },
    'validate': {'format': '-f'}
})


def cmd(action: str, flags: set[str] = [], args: dict[str, str] = {}, gossfile: Path = Path.cwd()) -> list[str]:
    """constructs a list representing the goss command to execute"""
    # verify command
    if action not in {**FLAGS_MAP, **ARGS_MAP}:
        raise RuntimeError(f"Unsupported GoSS action attempted: {action}")

    # initialize goss command
    command: list[str] = ['goss']

    # check universal args
    # check if vars is specified
    if 'vars' in args:
        # verify vars file exists
        if Path(args['vars']).is_file():
            command.extend(['--vars', args['vars']])
            # remove vars from args to avoid doublecheck with action args
            del args['vars']
        else:
            raise FileNotFoundError(f"Vars file does not exist: {args['vars']}")
    # check if gossfile is default so we use implicit cwd within goss cli instead of module logic
    if gossfile == Path.cwd():
        command.append(action)
    else:
        if Path(gossfile).is_file():
            # the gossfile argument is universal and must be immediately specified before action
            command.extend(['-g', str(gossfile), action])
        else:
            # error if gossfile does not exist
            raise FileNotFoundError(f"GoSSfile does not exist: {gossfile}")

    # disable color if validate action
    if action == 'validate':
        command.append('--no-color')

    # construct list of goss flags
    # not all actions have flags, so return empty dict by default to shortcut to RuntimeError for unsupported flag if flag specified for action without flags
    action_flags_map: dict[str, str] = FLAGS_MAP.get(action, {})
    for flag in flags:
        if flag in action_flags_map:
            # add goss flag from corresponding module flag in FLAGS
            command.append(action_flags_map[flag])
        else:
            # unsupported flag specified
            raise RuntimeError(f"Unsupported GoSS flag specified: {flag}")

    # construct list of goss args
    # not all actions have args, so return empty dict by default to shortcut to RuntimeError for unsupported arg if arg specified for action without args
    action_args_map: dict[str, str] = ARGS_MAP.get(action, {})
    for arg, arg_value in args.items():
        # verify this is a valid action argument
        if arg in action_args_map:
            # port arg requires int-->str and : prefix
            if arg == 'port':
                arg_value = f":{arg_value}"
            # append the value interpolated with the arg name from the dict to the command
            command.extend([action_args_map[arg], arg_value])
        else:
            # unsupported arg specified
            raise RuntimeError(f"Unsupported GoSS arg specified: {arg}")

    return command
