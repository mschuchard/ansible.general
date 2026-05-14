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
    gateway:
        description: Gateway URL starting with http(s)://
        required: false
        default: http://127.0.0.1:8080
        type: str
        new_in_version: "1.4.2"
    instance:
        description: Print the function instance name/id
        required: false
        default: false
        type: bool
    lines:
        description: Number of recent log lines to display. Unlimited if <= 0.
        required: false
        default: -1
        type: int
        new_in_version: "1.4.2"
    name:
        description: Name of the function to fetch logs for
        required: true
        type: str
    namespace:
        description: Namespace of the function
        required: false
        type: str
        new_in_version: "1.4.2"
    output:
        description: Output logs in the specified format
        required: false
        type: str
        choices: ['plain', 'keyvalue', 'json']
        new_in_version: "1.4.2"
    print_name:
        description: Print the function name in the log output
        required: false
        default: false
        type: bool
        new_in_version: "1.4.2"
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    since:
        description: Return logs newer than a relative duration like 5s
        required: false
        type: str
        new_in_version: "1.4.2"
    since_time:
        description: Include logs since the given timestamp (RFC3339)
        required: false
        type: str
        new_in_version: "1.4.2"
    tail:
        description: Tail logs and continue printing new logs until the end of the request, up to 30s.
        required: false
        default: true
        type: bool
        new_in_version: "1.4.2"
    time_format:
        description: String format for the timestamp as a Go time format string. Empty will not print the timestamp.
        required: false
        type: str
        new_in_version: "1.4.2"
    tls_no_verify:
        description: Disable TLS validation
        required: false
        default: false
        type: bool
        new_in_version: "1.4.2"
    token:
        description: Pass a JWT token to use instead of basic auth
        required: false
        type: str
        new_in_version: "1.4.2"

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# fetch logs with instance and function names
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
    name: my-function

# fetch logs in JSON format with last 5 lines
- name: Fetch the last 5 log lines in JSON format
  mschuchard.general.faas_logs:
    name: my-function
    output: json
    lines: 5

# fetch logs since a relative duration without tailing
- name: Fetch logs from the past 10 minutes without tailing
  mschuchard.general.faas_logs:
    name: my-function
    since: 10m
    tail: false

# fetch logs from a remote gateway with TLS disabled and a JWT token
- name: Fetch logs from a remote gateway
  mschuchard.general.faas_logs:
    name: my-function
    gateway: https://faas.example.com:8080
    tls_no_verify: true
    token: my-jwt-token
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
    """primary function for faas logs module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'config_file': {'type': 'path', 'required': False},
            'filter': {'type': 'str', 'required': False},
            'gateway': {'type': 'str', 'required': False, 'new_in_version': '1.4.2'},
            'instance': {'type': 'bool', 'required': False, 'default': False},
            'lines': {'type': 'int', 'required': False, 'new_in_version': '1.4.2'},
            'name': {'type': 'str', 'required': True},
            'namespace': {'type': 'str', 'required': False, 'new_in_version': '1.4.2'},
            'output': {'type': 'str', 'required': False, 'choices': ['plain', 'keyvalue', 'json'], 'new_in_version': '1.4.2'},
            'print_name': {'type': 'bool', 'required': False, 'default': False, 'new_in_version': '1.4.2'},
            'regex': {'type': 'str', 'required': False},
            'since': {'type': 'str', 'required': False, 'new_in_version': '1.4.2'},
            'since_time': {'type': 'str', 'required': False, 'new_in_version': '1.4.2'},
            'tail': {'type': 'bool', 'required': False, 'default': True, 'new_in_version': '1.4.2'},
            'time_format': {'type': 'str', 'required': False, 'new_in_version': '1.4.2'},
            'tls_no_verify': {'type': 'bool', 'required': False, 'default': False, 'new_in_version': '1.4.2'},
            'token': {'type': 'str', 'required': False, 'new_in_version': '1.4.2'},
        },
        mutually_exclusive=[('since', 'since_time')],
        supports_check_mode=True,
    )

    # check optional flags
    flags: set[str] = set()
    if module.params.get('instance'):
        flags.add('instance')
    if module.params.get('print_name'):
        flags.add('print_name')
    if module.params.get('tail') is False:
        flags.add('tail')
    if module.params.get('tls_no_verify'):
        flags.add('tls_no_verify')

    # check on optional args
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # determine faas command
    command: list[str] = faas.cmd(action='logs', flags=flags, args=flags_args[1])

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
