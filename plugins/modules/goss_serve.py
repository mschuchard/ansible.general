#!/usr/bin/python
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import goss


DOCUMENTATION = r'''
---
module: goss_serve

short_description: Module to serve a GoSS health endpoint.

version_added: "1.0.0"

description: Serve a GoSS health endpoint for validating systems.

options:
    endpoint:
        description: Endpoint to expose.
        required: false
        default: /healthz
        type: str
    format:
        description: Output format for validation report.
        required: false
        default: rspecish
        type: str
    gossfile:
        description: The specific gossfile used for serveing the output.
        required: false
        default: `cwd`/goss.yaml
        type: str
    port:
        description: Address to listen on.
        required: false
        default: 8080
        type: str
    vars:
        description: Path to YAMl or JSON format file containing variables for template.
        required: false
        type: bool

requirements:
    - goss >= 0.3.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# serve a health endpoint with a gossfile at /path/to/my_gossfile.yaml
- name: Serve a health endpoint with a gossfile at /path/to/my_gossfile.yaml
  mschuchard.general.goss_serve:
    gossfile: /path/to/my_gossfile.yaml

# serve a health endpoint with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
- name: Serve a health endpoint with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
  mschuchard.general.goss_serve:
    format: json
    vars: /path/to/vars.yaml

# serve a health endpoint with a default location gossfile at localhost:8765/check
- name: Serve a health endpoint with a default location gossfile at localhost:8765/check
  mschuchard.general.goss_serve:
    endpoint: /check
    port: 8765
'''

RETURN = r'''
TODO
'''


def run_module() -> None:
    """primary function for goss serve module"""
    


def main() -> None:
    """module entrypoint"""
    run_module()


if __name__ == '__main__':
    main()
