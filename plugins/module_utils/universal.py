"""universal module utilities"""

__metaclass__ = type

import json
import warnings
from pathlib import Path
import yaml


def action_flags_command(command: list[str], flags: set[str] = set(), action_flags_map: dict[str, str] = {}) -> list[str]:
    """convert action flags dict into list of command strings
    this is commonly used in the module_utils"""
    # in this function command list is mutable pseudo-reference and also returned

    # not all actions have flags, so input empty dict by default for the map to shortcut to RuntimeWarning for unsupported flag if flag specified for action without flags
    # iterate through input parameter flags
    for flag in flags:
        if flag in action_flags_map:
            # add tool flag from corresponding module flag in FLAGS
            command.append(action_flags_map[flag])
        else:
            # unsupported flag specified
            warnings.warn(f'Unsupported flag specified: {flag}', RuntimeWarning)

    return command


def validate_json_yaml_file(file: Path) -> bool:
    """validate a file contains valid json and therefore also valid yaml"""
    # load the file
    content: str = Path(file).read_text(encoding='UTF-8')

    try:
        # verify its decoded json contents
        if json.loads(content) is not None:
            return True

        return False
    # it is not json
    except ValueError:
        try:
            # verify its decoded yaml contents
            if isinstance(yaml.safe_load(content), object):
                return True

            return False

        # raise error for file with invalid yaml/json contents
        except yaml.YAMLError as exc:
            warnings.warn(f'Specified YAML or JSON file does not contain valid YAML or JSON: {file}', SyntaxWarning)
            raise ValueError(exc) from exc


def vars_converter(var_pairs: dict[str, list | dict | str]) -> list[str]:
    """convert an ansible param dict of var name-value pairs to a hashi list of var name-value pairs"""

    # transform dict[<var name>, <var value>] into list["<var name>='<var value>'"] where <var value> is JSON encoded if complex type
    var_strings: list[str] = []
    # iterate through var names and values within pairs
    for var, values in var_pairs.items():
        # if the value is a complex type then encode to compact JSON for cli parsing
        if isinstance(values, list) or isinstance(values, dict):
            var_strings.append(f"{var}='{json.dumps(values, separators=(',', ':'))}'")
        # if the value is a primitive type then handle normally
        else:
            var_strings.append(f"{var}='{values}'")

    # transform list["<var name>=<var value>"] into list with "-var" element followed by "<var name>=<var value>" element
    # various language limitations force this non-ideal implementation
    return ' '.join([f'-var {var_value}' for var_value in var_strings]).split()


def var_files_converter(var_files: list[Path]) -> list[str]:
    """convert an ansible param list of var files to a hashi list of var files"""

    # initialize args
    args: list[str] = []

    # iterate through var_files and convert
    for var_file in var_files:
        # verify vars file exists before conversion
        if Path(var_file).is_file():
            args.append(f'-var-file={var_file}')
        else:
            raise FileNotFoundError(f'Var file does not exist: {var_file}')

    return args


def params_to_flags_args(params: dict, spec: dict[str, dict]) -> tuple[set[str], dict]:
    """function to convert ansible module params to module utility action flags and args
    subtleties in specific module params prevent this from widespread use
    params dictionary argument should be populated from AnsibleModule.params{}, and spec from AnsibleModule.argument_spec{}"""

    # initialize
    flags: set[str] = set()
    args: dict = {}

    # iterate through populated params
    for param, attribute in params.items():
        # check if parameter value is defined
        if attribute:
            # check module argument spec for parameter type
            match spec[param]['type']:
                # check if bool type --> probably flag
                case 'bool':
                    flags.add(param)
                # check if path type --> probably need type conversion
                case 'path':
                    args.update({param: Path(attribute)})
                # otherwise generic argument
                case _:
                    args.update({param: attribute})

    return flags, args
