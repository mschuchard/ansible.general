"""terraform module utilities"""
__metaclass__ = type

import warnings
from typing import Final
from pathlib import Path
import itertools
from mschuchard.general.plugins.module_utils import universal


# dictionary that maps input args to terraform flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'apply': {
        'destroy': '-destroy',
    },
    'fmt': {
        'check': '-check',
        'diff': '-diff',
        'recursive': '-recursive',
    },
    'init': {
        'force_copy': '-force-copy',
        'migrate_state': '-migrate-state',
        'upgrade': '-upgrade',
    },
    'plan': {
        'destroy': '-destroy',
        'refresh_only': '-refresh-only'
    },
    'test': {
        'json': '-json',
    },
    'validate': {
        'json': '-json',
    },
})

# dictionary that maps input args to terraform args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict({
    'apply': {
        'target': '',
        'var': '',
        'var_file': '',
    },
    'fmt': {
        'write': '-write=',
    },
    'init': {
        'backend': '-backend=', # tf cli treats as arg despite only accepting bool inputs
        'backend_config': '',
        'plugin_dir': '',
    },
    'import': {
        'resource': '',
        'var': '',
        'var_file': '',
    },
    'plan': {
        'generate_config': '-generate-config-out=',
        'out': '-out=',
        'replace': '',
        'target': '',
        'var': '',
        'var_file': '',
    },
    'test': {
        'cloud_run': '-cloud-run=',
        'filter': '',
        'test_dir': '-test-directory=',
        'var': '',
        'var_file': '',
    },
    'validate': {
        'test_dir': '-test-directory=',
    }
})


def cmd(action: str, flags: set[str] = [], args: dict[str, str | list[str]] = {}, target_dir: Path = Path.cwd()) -> list[str]:
    """constructs a list representing the terraform command to execute"""

    # alias destroy to apply with destroy flag
    if action == 'destroy':
        action = 'apply'
        flags.append('destroy')
    # verify command
    elif action not in ARGS_MAP:
        raise RuntimeError(f"Unsupported Terraform action attempted: {action}")

    # initialize terraform command
    command: list[str] = ['terraform']

    # validate the target config dir
    if not Path(target_dir).is_dir():
        # otherwise error if it is not an existing directory
        raise RuntimeError(f"Targeted directory does not exist: {target_dir}")

    # change directory if target_dir is not cwd (must be arg to base command)
    if target_dir != Path.cwd():
        command.append(f"-chdir={target_dir}")

    # further initialize terraform command
    command += [action, '-no-color']
    if action in ['apply', 'init', 'plan', 'import']:
        command.append('-input=false')
    elif action == 'fmt':
        command.append('-list=false')

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
            # if the arg value is a str or bool, then append the value interpolated with the arg name from the dict to the command
            if (isinstance(arg_value, str) or isinstance(arg_value, bool)) and len(action_args_map[arg]) > 0:
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

    return command


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
                    # append kv pair from dict
                    if isinstance(backend_config, dict):
                        # transform dict into str
                        args['backend_config'].append(f"-backend-config='{list(backend_config.keys())[0]}={list(backend_config.values())[0]}'")
                    # otherwise is a hcl file path
                    elif isinstance(backend_config, str):
                        # append path to hcl file
                        if Path(backend_config).is_file():
                            args['backend_config'].append(f"-backend-config={backend_config}")
                        # file not found at input path
                        else:
                            raise FileNotFoundError(f"Backend config file does not exist: {backend_config}")
                    # otherwise this
                    else:
                        # invalid type in element
                        warnings.warn(f"backend_config element value '{backend_config}' is not a valid type; must be string for file path, or dict for key-value pair", RuntimeWarning)

            # list[str] to list[str] with "-plugin-dir=" prefixed
            case 'plugin_dir':
                # reset arg because file check does not allow generator pattern
                args['plugin_dir'] = []

                for plugin_dir in arg_value:
                    # verify plugin_dir is existing dir before conversion
                    if Path(plugin_dir).is_dir():
                        args['plugin_dir'].append(f"-plugin-dir={plugin_dir}")
                    else:
                        raise FileNotFoundError(f"Plugin directory does not exist: {plugin_dir}")
            # list[str] to list[str] with "-<arg>=" prefixed (relies on isomorphism between module and terraform args)
            case 'filter' | 'replace' | 'target':
                # generate list of argument strings
                args[arg] = [f"-{arg}={value}" for value in arg_value]
                print(args[arg])
            # dict[str, str] to space delimited list[str]
            # is extensible for possible future functionality whereby a "resources" module param is input with key-address value-id
            case 'resource':
                # generate list of address and id
                # args[arg] = [f"'{address}' {id}" for address, id in arg_value.items()]
                # below for single resource also requires flattening
                # address should not require shell string cast since executed as ansible command and not in shell interpreter
                args[arg] = list(itertools.chain.from_iterable([[address, id] for address, id in arg_value.items()]))
            # list[dict[str, str]] to "key=value" string with args for n>1 values
            case 'var':
                # assign converted value to var key
                args['var'] = universal.vars_converter(arg_value)
            # list[str] to list[str] with "-var-file=" prefixed
            case 'var_file':
                # assign converted value to var_file key
                args['var_file'] = universal.var_files_converter(arg_value)

    return args
