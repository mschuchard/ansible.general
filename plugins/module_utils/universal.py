"""universal module utilities"""
__metaclass__ = type

import json
import warnings
from pathlib import Path
import yaml


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


def var_files_converter(var_files: list[str]) -> list[str]:
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
