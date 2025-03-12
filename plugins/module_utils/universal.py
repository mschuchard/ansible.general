"""universal module utilities"""
__metaclass__ = type

import json
import warnings
from pathlib import Path
import yaml


def action_flags_command(command: list[str], flags: set[str] = [], action_flags_map: dict[str, str] = {}) -> list[str]:
    """convert action flags dict into list of command strings"""
    # in this function command list is mutable pseudo-reference and also returned

    # not all actions have flags, so input empty dict by default for the map to shortcut to RuntimeWarning for unsupported flag if flag specified for action without flags
    # iterate through input parameter flags
    for flag in flags:
        if flag in action_flags_map:
            # add packer flag from corresponding module flag in FLAGS
            command.append(action_flags_map[flag])
        else:
            # unsupported flag specified
            warnings.warn(f"Unsupported flag specified: {flag}", RuntimeWarning)

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
            warnings.warn(f"Specified YAML or JSON file does not contain valid YAML or JSON: {file}", SyntaxWarning)
            raise ValueError(exc) from exc


def vars_converter(var_pairs: list[dict[str, str]]) -> list[str]:
    """convert an ansible param list of dict var name-value pairs to a hashi list of var name-value pairs"""

    # transform list[dict[<var name>, <var value>]] into list["<var name>=<var value>"]
    var_strings: list[str] = [f"{list(var_pair.keys())[0]}={list(var_pair.values())[0]}" for var_pair in var_pairs]

    # transform list["<var name>=<var value>"] into list with "-var" element followed by "<var name>=<var value>" element
    # various language limitations force this non-ideal implementation
    return ' '.join([f"-var {var_value}" for var_value in var_strings]).split()


def var_files_converter(var_files: list[Path]) -> list[str]:
    """convert an ansible param list of var files to a hashi list of var files"""

    # initialize args
    args = []

    # iterate through var_files and convert
    for var_file in var_files:
        # verify vars file exists before conversion
        if Path(var_file).is_file():
            args.append(f"-var-file={var_file}")
        else:
            raise FileNotFoundError(f"Var file does not exist: {var_file}")

    return args


def params_to_flags_args(params: dict, spec: dict[str, dict]) -> (list[str], dict):
    """theoretical function to convert ansible module params to module utility action flags and args
    subtleties in specific module params prevent this from widespread use
    params dictionary argument should be populated from AnsibleModule.params{}, and spec from AnsibleModule.argument_spec{}"""

    # initialize
    flags: list[str] = []
    args: dict = {}

    # iterate through populated params
    for param, attribute in params.items():
        # check if bool type and value input
        if spec[param]['type'] == 'bool' and attribute:
            flags.append(param)
        # otherwise argument if value input
        elif attribute:
            args.update({param: attribute})

    return flags, args
