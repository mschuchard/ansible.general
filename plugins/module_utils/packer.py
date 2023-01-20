"""packer module utilities"""
__metaclass__ = type

from typing import Final
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
    'validate': {'syntax-only': '-syntax-only'},
})

# dictionary that maps input args to packer args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'build': {
        'except': '-except=',
        'only': '-only=',
        'on_error': '-on-error=',
        'parallel_builds': '-parallel-builds=',
        'var': '-var ',
        'var_file': '-var-file='
    },
    'validate': {
        'except': '-except=',
        'only': '-only=',
        'var': '-var ',
        'var_file': '-var-file='
    },
})


def cmd(action: str, flags: set[str] = [], args: dict[str, str] = {}, target_dir: str = Path.cwd()) -> list[str]:
    """constructs a list representing the packer command to execute"""
    # verify command
    if action not in FLAGS_MAP:
        raise RuntimeError(f"Unsupported Packer action attempted: {action}")

    # initialize packer command
    cmd: list[str] = ['packer', action, '-machine-readable', '-color=false']

    # construct list of packer flags
    action_flags_map: dict[str, str] = FLAGS_MAP[action]
    for flag in flags:
        if flag in action_flags_map:
            # add packer flag from corresponding module flag in FLAGS
            cmd.append(action_flags_map[flag])
        else:
            # unsupported flag specified
            raise RuntimeError(f"Unsupported Packer flag specified: {flag}")

    # construct list of packer args
    # not all actions have args, so return empty list to shortcut to RuntimeError for unpported arg if arg specified for action without args
    action_args_map: dict[str, str] = ARGS_MAP.get(action, [])
    for arg, arg_value in args.items():
        if arg in action_args_map:
            # add packer arg from corresponding module arg in ARGS
            cmd.append(f"{action_args_map[arg]}{arg_value}")
        else:
            # unsupported arg specified
            raise RuntimeError(f"Unsupported Packer arg specified: {arg}")

    # return the command with the target dir appended
    if Path(target_dir).exists():
        return cmd + [target_dir]

    # otherwise error if it does not exist (possible to target file or dir)
    raise RuntimeError(f"Targeted directory or file does not exist: {target_dir}")


def ansible_to_packer(args: dict) -> str:
    """converts ansible types and syntax to packer types and formatting"""
    # in this function args dict is mutatable pseudo-reference and also returned
    # iterate through ansible module argument
    for arg, arg_value in args.items():
        # list[str] to comma-delimited string
        if arg in ['except', 'only']:
            args[arg] = arg_value.join(',')
        # list[dict[str, str]] to "key=value" string, TODO: finish
        elif arg in ['var']:
            args[arg] = f"{arg_value}={arg_value}"
        # list[str] to ?, TODO: finish
        elif arg in ['var_file']:
            args[arg] = arg_value
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
