#!/usr/bin/python
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import goss


DOCUMENTATION = r'''
---
module: goss_validate

short_description: Module to validate a system with a gossfile.

version_added: "1.0.0"

description: Validate a system with a gossfile or gossfiles.

options:
    format:
        description: Output format for validation report.
        required: false
        default: rspecish
        type: str
    gossfile:
        description: The specific gossfile used for validateing the output.
        required: false
        default: `cwd`/goss.yaml
        type: str
    vars:
        description: Additionally validate the golang template prior to validateing the gossfile.
        required: false
        default: false
        type: bool

requirements:
    - goss >= 0.3.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# validate a system with a gossfile at /path/to/my_gossfile.yaml
- name: Validate a system with a gossfile at /path/to/my_gossfile.yaml
  mschuchard.general.goss_validate:
    gossfile: /path/to/my_gossfile.yaml

# validate a system with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
- name: Validate a system with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
  mschuchard.general.goss_validate:
    format: json
    vars: /path/to/vars.yaml
'''

RETURN = r'''
TODO
'''


def run_module() -> None:
    


def main() -> None:
    """module entrypoint"""
    run_module()


if __name__ == '__main__':
    main()
