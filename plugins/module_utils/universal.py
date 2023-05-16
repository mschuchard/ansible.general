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
