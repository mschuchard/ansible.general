#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform validate"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: terraform_validate

short_description: Module to validate Terraform module configuration directories and files.

version_added: "1.1.0"

description: Validates the configuration files in a directory; referring only to the configuration and not accessing any remote services such as remote state, provider APIs, etc. Validate runs checks that verify whether a configuration is syntactically valid and internally consistent. This is regardless of any provided variables or existing state. It is thus primarily useful for general verification of reusable modules. This includes correctness of attribute names and value types.

options:
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    json:
        description: Machine readable output will be output to stdout in JSON format.
        required: false
        type: bool
    test_dir:
        description: Set the Terraform test directory.
        required: false
        default: tests
        type: path


requirements:
    - terraform >= 1.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# execute validation in /path/to/terraform_config_dir
- name: Execute validation in /path/to/terraform_config_dir
  mschuchard.general.terraform_validate:
    config_dir: /path/to/terraform_config_dir

# execute validation for current directory with json output and custom test directory
- name: Execute validation for current directory with json output and custom test directory
  mschuchard.general.terraform_validate:
    json: true
    test_dir: 'my_tests'
"""

RETURN = r"""
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform validate -json'
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import terraform


def main() -> None:
    """primary function for terraform validate module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'json': {'type': 'bool', 'required': False},
            'test_dir': {'type': 'path', 'required': False},
        },
        supports_check_mode=True,
    )

    # initialize
    config_dir: Path = Path(module.params.get('config_dir'))
    test_dir: list[str] = module.params.get('test_dir')

    # check flags
    flags: set[str] = set()
    if module.params.get('json'):
        flags.add('json')

    # check args
    args: dict = {}
    if test_dir:
        args.update({'test_dir': test_dir})

    # convert ansible params to terraform args
    args = terraform.ansible_to_terraform(args)

    # determine terraform command
    command: list[str] = terraform.cmd(action='validate', flags=flags, args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute terraform
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir, environ_update={'TF_IN_AUTOMATION': 'true'})

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
