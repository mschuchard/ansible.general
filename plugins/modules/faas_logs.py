#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for faas logs"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: faas_logs

short_description: Module to fetch logs for a FaaS function.

version_added: "1.4.0"

description: Fetches logs for a given OpenFaaS function name in plain text or JSON format.

options:
    config_file:
        description: Path to YAML file describing function(s)
        required: false
        type: path
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    instance:
        description: Print the function instance name/id
        required: false
        default: false
        type: bool
    name:
        description: Name of the function to fetch logs for
        required: true
        type: str
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# fetch logs in with instance and function names
- name: Fetch logs with instance and function names
  mschuchard.general.faas_logs:
    name: my-function
    instance: true

# fetch logs from a stack.yaml file with filter and regex
- name: Fetch logs from a stack.yaml file with filter and regex
  mschuchard.general.faas_logs:
    config_file: stack.yaml
    filter: '*gif*'
    regex: 'fn[0-9]_.*'
"""

RETURN = r"""
command:
    description: The raw FaaS CLI command executed by Ansible.
    type: str
    returned: always
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import faas, universal


def main() -> None:
    """primary function for faas logs module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'config_file': {'type': 'path', 'required': False},
            'filter': {'type': 'str', 'required': False},
            'instance': {'type': 'bool', 'required': False, 'default': False},
            'name': {'type': 'str', 'required': True},
            'regex': {'type': 'str', 'required': False},
        },
        supports_check_mode=True,
    )

    # check on optional flags and args
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # determine faas command
    command: list[str] = faas.cmd(action='logs', flags=flags_args[0], args=flags_args[1])

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute faas
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=str(Path.cwd()))

    # post-process
    if return_code == 0:
        module.exit_json(changed=False, stdout=stdout, stderr=stderr, command=command)
    else:
        module.fail_json(
            msg=stderr.rstrip(),
            return_code=return_code,
            cmd=command,
            stdout=stdout,
            stdout_lines=stdout.splitlines(),
            stderr=stderr,
            stderr_lines=stderr.splitlines(),
        )


if __name__ == '__main__':
    main()
