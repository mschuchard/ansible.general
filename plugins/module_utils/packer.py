"""packer module utilities"""
__metaclass__ = type

from typing import Dict, List, Set, Final
from pathlib import Path


# dictionary that maps input args to packer flags and args
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


def packer_cmd(action: str, flags: Set[str] = [], target_dir: str = Path.cwd()) -> List[str]:
    """constructs a list representing the packer command to execute"""
    # verify command
    if action not in ['init', 'fmt', 'validate', 'build']:
        raise RuntimeError(f"Unsupported Packer action attempted: {action}")

    # initialize packer command
    cmd: List[str] = ['packer', action, '-machine-readable', '-color=false']

    # construct list of packer args and flags
    action_flags_map: Dict[str, str] = FLAGS_MAP[action]
    for flag in flags:
        if flag in action_flags_map:
            # add packer arg or flag from corresponding module arg in ARGS
            cmd.append(action_flags_map[flag])
        else:
            # unsupported arg specified
            raise RuntimeError(f"Unknown Packer flag specified: {flag}")

    # return the command with the target dir appended
    if Path(target_dir).exists():
        return cmd + [target_dir]

    # otherwise error if it does not exist (possible to target file or dir)
    raise RuntimeError(f"Targeted directory or file does not exist: {target_dir}")
