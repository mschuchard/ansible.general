"""terraform module utilities"""
__metaclass__ = type

import re
import warnings
from typing import Final
from pathlib import Path


# dictionary that maps input args to terraform flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'init': {
        'force_copy': '-force-copy',
        'migrate_state': '-migrate-state',
        'upgrade': '-upgrade',
    },
})

# dictionary that maps input args to terraform args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'init': {
        'backend': '-backend=',
        'backend_config': '',
        'plugin_dir': '-plugin-dir=',
    },
})


def cmd(action: str, flags: set[str] = [], args: dict[str, str | list[str]] = {}, target_dir: Path = Path.cwd()) -> list[str]:
    """constructs a list representing the terraform command to execute"""
    # verify command
    if action not in FLAGS_MAP:
        raise RuntimeError(f"Unsupported Terraform action attempted: {action}")

    # initialize terraform command
    command: list[str] = ['terraform', action, '-no-color']
    if action in ['init']:
        command.append('-input=false')

    # not all actions have flags, so return empty dict by default to shortcut to RuntimeError for unsupported flag if flag specified for action without flags
    action_flags_map: dict[str, str] = FLAGS_MAP.get(action, {})
    for flag in flags:
        if flag in action_flags_map:
            # add packer flag from corresponding module flag in FLAGS
            command.append(action_flags_map[flag])
        else:
            # unsupported flag specified
            warnings.warn(f"Unsupported Terraform flag specified: {flag}", RuntimeWarning)

    # construct list of terraform args
    # not all actions have args, so return empty dict by default to shortcut to RuntimeError for unsupported arg if arg specified for action without args
    action_args_map: dict[str, str] = ARGS_MAP.get(action, {})
    for arg, arg_value in args.items():
        # verify this is a valid action argument
        if arg in action_args_map:
            # note for next two conditionals second logical tests for whether str or list is expected based on pseudo-schema in ARGS_MAP
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
            warnings.warn(f"Unsupported Terraform arg specified: {arg}", RuntimeWarning)

    # return the command with an additional arg to change into the target dir
    if Path(target_dir).is_dir():
        command.append(f"-chdir={target_dir}")
        return command

    # otherwise error if it is not an existing directory
    raise RuntimeError(f"Targeted directory does not exist: {target_dir}")


def ansible_to_terraform(args: dict) -> dict[str, (str, list[str])]:
    """converts ansible types and syntax to terraform types and formatting for arguments only"""
    # in this function args dict is mutable pseudo-reference and also returned
    # iterate through ansible module argument
    for arg, arg_value in args.items():
        match arg:
            # list[str] to list[str] with "-backend-config=" prefixed
            case 'backend_config':
                # reset arg because file check does not allow generator pattern
                args['backend_config'] = []

                for backend_config in arg_value:
                    # verify backend_config is either kv pair or existing file before conversion
                    if re.search(r'\w+=\w+', backend_config) or Path(backend_config).is_file():
                        args['backend_config'].append(f"-backend-config={backend_config}")
                    else:
                        # TODO f string bug is dropping all but first char
                        raise FileNotFoundError(f"Backend config file does not exist: {backend_config}")

    return args
