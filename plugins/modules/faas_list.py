#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for faas list"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: faas_list

short_description: Module to list FaaS functions.

version_added: "1.4.0"

description: Lists OpenFaaS functions either on a local or remote gateway.

options:
    config_file:
        description: Path to YAML file describing function(s)
        required: false
        type: path
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    sort:
        description: Sort the functions by "name" or "invocations"
        required: false
        default: name
        type: str
        choices: ['name', 'invocations']
    verbose:
        description: Verbose output for the function list
        required: false
        default: false
        type: bool

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# list functions from a stack.yaml file with filter and regex
- name: List functions from a stack.yaml file with filter and regex
  mschuchard.general.faas_list:
    config_file: stack.yaml
    filter: '*gif*'
    regex: 'fn[0-9]_.*'

# list functions sorted by invocations
- name: List functions sorted by invocations with verbose output
  mschuchard.general.faas_list:
    sort: invocations
    verbose: true
"""

RETURN = r"""
command:
    description: The raw FaaS CLI command executed by Ansible.
    type: str
    returned: always
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import faas


def main() -> None:
    """primary function for faas list module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'config_file': {'type': 'path', 'required': False},
            'filter': {'type': 'str', 'required': False},
            'regex': {'type': 'str', 'required': False},
            'sort': {'type': 'str', 'required': False, 'default': 'name', 'choices': ['name', 'invocations']},
            'verbose': {'type': 'bool', 'required': False, 'default': False},
        },
        supports_check_mode=True,
    )

    # initialize
    filter: str = module.params.get('filter')
    regex: str = module.params.get('regex')
    config_file: Path = module.params.get('config_file')
    sort: str = module.params.get('sort')

    # check on optional flags
    flags: set[str] = set()
    if module.params.get('verbose'):
        flags.add('verbose')

    # check args
    args: dict = {}
    if filter:
        args.update({'filter': filter})
    if regex:
        args.update({'regex': regex})
    if config_file:
        args.update({'config_file': Path(config_file)})
    if sort != 'name':
        args.update({'sort': sort})

    # determine faas command
    command: list[str] = faas.cmd(action='list', flags=flags, args=args)

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
