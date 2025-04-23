"""faas module utilities"""

__metaclass__ = type


from typing import Final
from mschuchard.general.plugins.module_utils import universal

# dictionary that maps input args to terraform flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'build': {
            'disable_stack_pull': '--disable-stack-pull',
            'env_subst': '--envsubst',
            'no_cache': '--no-cache',
            'pull': '--pull',
            'quiet': '--quiet',
            'shrinkwrap': '--shrinkwrap',
        },
        'deploy': {},
        'invoke': {},
        'list': {},
        'login': {},
        'logs': {},
        'push': {},
        'remove': {},
    }
)

# dictionary that maps input args to terraform args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'build': {},
        'deploy': {},
        'invoke': {},
        'list': {},
        'login': {},
        'logs': {},
        'push': {},
        'remove': {},
    }
)


def cmd(action: str, flags: set[str] = [], args: dict[str, str] = {}, name: str = None) -> list[str]:
    """constructs a list representing the openfaas command to execute"""
    # verify command
    if action not in FLAGS_MAP:
        raise RuntimeError(f'Unsupported FaaS action attempted: {action}')

    # initialize faas-cli command
    command: list[str] = ['faas-cli', action]

    # append list of flag commands
    universal.action_flags_command(command, flags, FLAGS_MAP.get(action, {}))

    return command
