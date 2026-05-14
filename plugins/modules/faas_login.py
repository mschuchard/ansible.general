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
    gateway:
        description: Gateway URL starting with http(s)://
        required: false
        default: http://127.0.0.1:8080
        type: str
        new_in_version: "1.4.2"
    password:
        description: Gateway password
        required: false
        type: str
        no_log: true
    password_stdin:
        description: Reads the gateway password from stdin
        required: false
        default: false
        type: bool
        new_in_version: "1.4.2"
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    timeout:
        description: Override the timeout for this API call (duration string, e.g. '60s', '1m', '2m30s')
        required: false
        type: str
        new_in_version: "1.4.2"
    tls_no_verify:
        description: Disable TLS validation
        required: false
        default: false
        type: bool
        new_in_version: "1.4.2"
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

# log in to OpenFaaS gateway reading password from stdin
- name: Log in to OpenFaaS gateway reading password from stdin
  mschuchard.general.faas_login:
    password_stdin: true

# log in to OpenFaaS gateway with default username, and from a stack.yaml file with filter and regex
- name: Log in to OpenFaaS gateway with default username, and from a stack.yaml file with filter and regex
  mschuchard.general.faas_login:
    config_file: stack.yaml
    filter: '*gif*'
    regex: 'fn[0-9]_.*'

# log in to a remote OpenFaaS gateway with TLS disabled and a custom timeout
- name: Log in to a remote OpenFaaS gateway with TLS disabled and a custom timeout
  mschuchard.general.faas_login:
    gateway: https://openfaas.mydomain.com
    password: mypassword
    tls_no_verify: true
    timeout: 30s
"""

RETURN = r"""
command:
    description: The raw FaaS CLI command executed by Ansible.
    type: str
    returned: always
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mschuchard.general.plugins.module_utils import faas, universal


def main() -> None:
    """primary function for faas login module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'config_file': {'type': 'path', 'required': False},
            'filter': {'type': 'str', 'required': False},
            'gateway': {'type': 'str', 'required': False, 'new_in_version': '1.4.2'},
            'password': {'type': 'str', 'required': False, 'no_log': True},
            'password_stdin': {'type': 'bool', 'required': False, 'default': False, 'new_in_version': '1.4.2'},
            'regex': {'type': 'str', 'required': False},
            'timeout': {'type': 'str', 'required': False, 'new_in_version': '1.4.2'},
            'tls_no_verify': {'type': 'bool', 'required': False, 'default': False, 'new_in_version': '1.4.2'},
            'username': {'type': 'str', 'required': False, 'default': 'admin'},
        },
        mutually_exclusive=[('password', 'password_stdin')],
        required_one_of=[('password', 'password_stdin')],
        supports_check_mode=True,
    )

    # check flags and args
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
