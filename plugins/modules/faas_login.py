#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for faas login"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: faas_login

short_description: Module to log in to OpenFaaS gateway.

version_added: "1.4.0"

description: Logs in to OpenFaaS gateway. If no gateway is specified, then the default value will be used.

options:
    config_file:
        description: Path to YAML file describing function(s)
        required: false
        type: path
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    password:
        description: Gateway password
        required: true
        type: str
        no_log: true
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    username:
        description: Gateway username
        required: false
        default: admin
        type: str

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# log in to OpenFaaS gateway with custom username
- name: Log in to OpenFaaS gateway with custom username
  mschuchard.general.faas_login:
    username: customuser
    password: mypassword

# log in to OpenFaaS gateway with default username, and from a stack.yaml file with filter and regex
- name: Log in to OpenFaaS gateway with default username, and from a stack.yaml file with filter and regex
  mschuchard.general.faas_login:
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
    """primary function for faas login module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'config_file': {'type': 'path', 'required': False},
            'filter': {'type': 'str', 'required': False},
            'password': {'type': 'str', 'required': True, 'no_log': True},
            'regex': {'type': 'str', 'required': False},
            'username': {'type': 'str', 'required': False, 'default': 'admin'},
        },
        supports_check_mode=True,
    )

    # check args
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # determine faas command
    command: list[str] = faas.cmd(action='login', flags=flags_args[0], args=flags_args[1])

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
        module.exit_json(changed=True, stdout=stdout, stderr=stderr, command=command)
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
