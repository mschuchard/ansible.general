"""packer module utilities"""
__metaclass__ = type

from typing import Dict, List, Set, Final
from pathlib import Path


# dictionary that maps input args to packer flags
FLAGS_MAP: Final[Dict[str, Dict[str, str]]] = dict({
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
ARGS_MAP: Final[Dict[str, Dict[str, str]]] = dict({
    'build': {},
    'validate': {
        'except': '-except',
        'only': '-only',
        'var': '-var',
        'var_file': '-var-file'
    },
})


def packer_cmd(action: str, flags: Set[str] = [], args: Dict[str, str] = {}, target_dir: str = Path.cwd()) -> List[str]:
    """constructs a list representing the packer command to execute"""
    # verify command
    if action not in FLAGS_MAP:
        raise RuntimeError(f"Unsupported Packer action attempted: {action}")

    # initialize packer command
    cmd: List[str] = ['packer', action, '-machine-readable', '-color=false']

    # construct list of packer flags
    action_flags_map: Dict[str, str] = FLAGS_MAP[action]
    for flag in flags:
        if flag in action_flags_map:
            # add packer flag from corresponding module flag in FLAGS
            cmd.append(action_flags_map[flag])
        else:
            # unsupported flag specified
            raise RuntimeError(f"Unknown Packer flag specified: {flag}")

    # construct list of packer args
    # not all actions have args, so return empty list to shortcut to RuntimeError for unpported arg if arg specified for action without args
    action_args_map: Dict[str, str] = ARGS_MAP.get(action, [])
    for arg in args:
        if arg in action_args_map:
            # add packer arg from corresponding module arg in ARGS
            cmd.append(action_args_map[arg])
        else:
            # unsupported arg specified
            raise RuntimeError(f"Unknown Packer arg specified: {arg}")

    # return the command with the target dir appended
    if Path(target_dir).exists():
        return cmd + [target_dir]

    # otherwise error if it does not exist (possible to target file or dir)
    raise RuntimeError(f"Targeted directory or file does not exist: {target_dir}")
