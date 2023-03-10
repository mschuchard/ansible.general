"""packer module utilities"""
__metaclass__ = type

from typing import Union, Final
from pathlib import Path


# dictionary that maps input args to packer flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'build': {
        'debug': '-debug',
        'force': '-force',
        'timestamp_ui': '-timestamp-ui',
    },
    'fmt': {
        'check': '-check',
        'recursive': '-recursive',
    },
    'init': {'upgrade': '-upgrade'},
    'validate': {'syntax_only': '-syntax-only'},
})

# dictionary that maps input args to packer args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'build': {
        'excepts': '-except=',
        'only': '-only=',
        'on_error': '-on-error=',
        'parallel_builds': '-parallel-builds=',
        'var': '',
        'var_file': ''
    },
    'validate': {
        'excepts': '-except=',
        'only': '-only=',
        'var': '',
        'var_file': ''
    },
})


def cmd(action: str, flags: set[str] = [], args: dict[str, Union[str, list[str]]] = {}, target_dir: Path = Path.cwd()) -> list[str]:
    """constructs a list representing the packer command to execute"""
    # verify command
    if action not in FLAGS_MAP:
        raise RuntimeError(f"Unsupported Packer action attempted: {action}")

    # initialize packer command
    command: list[str] = ['packer', action, '-machine-readable']
    if action == 'build':
        command.append('-color=false')

    # construct list of packer flags
    action_flags_map: dict[str, str] = FLAGS_MAP[action]
    for flag in flags:
        if flag in action_flags_map:
            # add packer flag from corresponding module flag in FLAGS
            command.append(action_flags_map[flag])
        else:
            # unsupported flag specified
            raise RuntimeError(f"Unsupported Packer flag specified: {flag}")

    # construct list of packer args
    # not all actions have args, so return empty dict by default to shortcut to RuntimeError for unpported arg if arg specified for action without args
    action_args_map: dict[str, str] = ARGS_MAP.get(action, {})
    for arg, arg_value in args.items():
        # verify this is a valid action argument
        if arg in action_args_map:
            # if the arg value is a str, then append the value interpolated with the arg name from the dict to the command
            if isinstance(arg_value, str) and len(action_args_map[arg]) > 0:
                command.append(f"{action_args_map[arg]}{arg_value}")
            # if the arg value is a list, then extend the command with the values because they are already formatted correctly
            elif isinstance(arg_value, list) and len(action_args_map[arg]) == 0:
                command.extend(arg_value)
            # if the arg value is some other type, or there was some unexpected mismatch between the arg name expecting a str/list and the other being provided, then something has gone wrong
            else:
                raise RuntimeError(f"Unexpected issue with argument name '{arg}' and argument value '{arg_value}'")
        else:
            # unsupported arg specified
            raise RuntimeError(f"Unsupported Packer arg specified: {arg}")

    # return the command with the target dir appended
    if Path(target_dir).exists():
        return command + [str(target_dir)]

    # otherwise error if it does not exist (possible to target file or dir)
    raise RuntimeError(f"Targeted directory or file does not exist: {target_dir}")


def ansible_to_packer(args: dict) -> dict[str, Union[str, list[str]]]:
    """converts ansible types and syntax to packer types and formatting for arguments only"""
    # in this function args dict is mutatable pseudo-reference and also returned
    # iterate through ansible module argument
    for arg, arg_value in args.items():
        # list[str] to comma-delimited string
        if arg in ['excepts', 'only']:
            args[arg] = ','.join(arg_value)
        # list[dict[str, str]] to "key=value" string with args for n>1 values
        elif arg in ['var']:
            # transform list[dict[<var name>, <var value>]] into list["<var name>=<var value>"]
            var_strings = [f"{list(var_pair.keys())[0]}={list(var_pair.values())[0]}" for var_pair in arg_value]
            # transform list["<var name>=<var value>"] into list with "-var" element followed by "<var name>=<var value>" element
            # various language limitations force this non-ideal implementation
            args[arg] = ' '.join([f"-var {var_value}" for var_value in var_strings]).split()
        # list[str] to list[str] with "-var-file=" prefixed
        elif arg in ['var_file']:
            args[arg] = [f"-var-file={var_file}" for var_file in args[arg]]
        # int to str
        elif arg in ['parallel_builds']:
            args[arg] = str(arg_value)
        # validate on_error arg value
        elif arg in ['on_error']:
            if arg_value not in ['cleanup', 'abort', 'ask', 'run-cleanup-provisioner']:
                raise RuntimeError(f"Unsupported on error argument value specified: {arg_value}")
        # unsupported argument
        else:
            raise RuntimeError(f"Unsupported Packer arg specified: {arg}")

    return args
