"""packer module utilities"""
__metaclass__ = type

from typing import List
from pathlib import Path


# dictionary that maps input args to packer flags and args
ARGS_MAP = dict({
    'check': '-check',
    'upgrade': '-upgrade',
})


def packer_cmd(action: str, target_dir: str, *args: str) -> List[str]:
    """constructs a list representing the packer command to execute"""
    # verify command
    if action not in ['init', 'fmt', 'validate', 'build']:
        raise RuntimeError(f"Unsupported Packer action attempted: {action}")

    # initialize packer command
    cmd: List[str] = ['packer', action, '-machine-readable']

    # construct list of packer args and flags
    for arg in *args:
        if arg in ARGS_MAP:
            # add packer arg or flag from corresponding module arg in ARGS
            cmd.append(ARGS_MAP[arg])
        else:
            # unsupported arg specified
            raise RuntimeError(f"Unknown Packer argument or flag specified: {arg}")

    # return the command with the target dir appended
    if Path(target_dir).exists():
        return cmd + [target_dir]

    # otherwise error if it does not exist (possible to target file or dir)
    raise RuntimeError(f"Targeted directory or file does not exist: {target_dir}")
