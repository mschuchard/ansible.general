"""terraform module utilities"""
__metaclass__ = type

from typing import Final
from pathlib import Path


# dictionary that maps input args to terraform flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'init': {
        'force_copy': '-migrate-state',
        'migrate_state': '-migrate-state',
        'upgrade': '-upgrade',
    },
})

# dictionary that maps input args to terraform args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'init': {
        'backend': '-backend=',
        'backend_configs': '', # can be list of str like var_file
        'plugin_dir': '-plugin-dir=',
    },
})


def cmd(action: str, flags: set[str] = [], args: dict[str, str | list[str]] = {}, target_dir: Path = Path.cwd()) -> list[str]:
    """constructs a list representing the terraform command to execute"""
    # verify command
    if action not in FLAGS_MAP:
        raise RuntimeError(f"Unsupported Packer action attempted: {action}")

    # initialize terraform command
    command: list[str] = ['terraform', action, '-no-color']
    if action in ['init']:
        command.append('-input=false')

    # return the command with an additional arg to change into the target dir
    if Path(target_dir).exists():
        command.append(f"-chdir={target_dir}")
        return command
