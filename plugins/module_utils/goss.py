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
    'build': {
        'endpoint': '-e',
        'format': '-f',
        'port': '-l',
        'vars': '--vars'
    },
    'validate': {
        'format': '-f',
        'vars': '--vars'
    },
})


def cmd(action: str, flags: set[str] = [], args: dict[str, str] = {}, gossfile: Path = Path.cwd()) -> list[str]:
    """constructs a list representing the goss command to execute"""
    # verify command
    if action not in FLAGS_MAP.update(ARGS_MAP):
        raise RuntimeError(f"Unsupported GoSS action attempted: {action}")

    # initialize goss command
    command: list[str] = ['goss', action]

    # construct list of goss flags
    action_flags_map: dict[str, str] = FLAGS_MAP[action]
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
            # append the value interpolated with the arg name from the dict to the command
            command.append(f"{action_args_map[arg]} {arg_value}")
        else:
            # unsupported arg specified
            raise RuntimeError(f"Unsupported GoSS arg specified: {arg}")

    # return the command with the target dir appended
    if Path(gossfile).exists():
        return command + ['-g', str(gossfile)]

    # otherwise error if it does not exist (possible to target file or dir)
    raise RuntimeError(f"GoSSfile does not exist: {gossfile}")
