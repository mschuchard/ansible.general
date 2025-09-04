#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform test"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: terraform_test

short_description: Module to manage Terraform automated integration tests against current configuration.

version_added: "1.1.0"

description: Executes automated integration tests against the current Terraform configuration. Terraform will search for .tftest.hcl files within the current configuration and testing directories. Terraform will then execute the testing run blocks within any testing files in order, and verify conditional checks and assertions against the created infrastructure. This command creates real infrastructure and will attempt to clean up the testing infrastructure on completion. Monitor the output carefully to ensure this cleanup process is successful.

options:
    cloud_run:
        description: Terraform will execute this test run remotely using HCP Terraform or Terraform Enterpise. You must specify the source of a module registered in a private module registry as the argument to this parameter. This allows Terraform to associate the cloud run with the correct HCP Terraform or Terraform Enterprise module and organization.
        required: false
        type: str
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    filter:
        description: Terraform will only execute the test files specified by this parameter.
        required: false
        type: list
        elements: path
    json:
        description: Machine readable output will be output to stdout in JSON format.
        required: false
        default: false
        type: bool
    test_dir:
        description: Set the Terraform test directory.
        required: false
        default: tests
        type: path
    var:
        description: Set values for one or more of the input variables in the root module of the configuration.
        required: false
        type: dict
    var_file:
        description: Load variable values from the given HCL2 files in addition to the default files terraform.tfvars and *.auto.tfvars.
        required: false
        type: list
        elements: path


requirements:
    - terraform >= 1.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# execute tests in /path/to/terraform_config_dir/my_tests
- name: Execute tests in /path/to/terraform_config_dir/my_tests
  mschuchard.general.terraform_test:
    config_dir: /path/to/terraform_config_dir
    test_dir: my_tests

# execute tests for current directory with json output and variable inputs
- name: Execute tests for current directory with json output and variable inputs
  mschuchard.general.terraform_test:
    json: true
    var:
      var_name: var_value
      var_name_other: var_value_other
    var_file:
    - one.tfvars
    - two.tfvars
"""

RETURN = r"""
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform test -json'
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import terraform


def main() -> None:
    """primary function for terraform test module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'cloud_run': {'type': 'str', 'required': False},
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'filter': {'type': 'list', 'elements': 'path', 'required': False},
            'json': {'type': 'bool', 'required': False},
            'test_dir': {'type': 'path', 'required': False},
            'var': {'type': 'dict', 'required': False},
            'var_file': {'type': 'list', 'elements': 'path', 'required': False},
        },
        supports_check_mode=True,
    )

    # initialize
    cloud_run: str = module.params.get('cloud_run')
    config_dir: Path = Path(module.params.get('config_dir'))
    filter: list[Path] = module.params.get('filter')
    test_dir: Path = module.params.get('test_dir')
    var: dict = module.params.get('var')
    var_file: list[Path] = module.params.get('var_file')

    # check flags
    flags: set[str] = set()
    if module.params.get('json'):
        flags.add('json')

    # check args
    args: dict = {}
    if cloud_run:
        args.update({'cloud_run': cloud_run})
    if filter:
        args.update({'filter': filter})
    if test_dir:
        args.update({'test_dir': Path(test_dir)})
    if var:
        args.update({'var': var})
    if var_file:
        args.update({'var_file': var_file})

    # convert ansible params to terraform args
    args = terraform.ansible_to_terraform(args)

    # determine terraform command
    command: list[str] = terraform.cmd(action='test', flags=flags, args=args, target_dir=config_dir)

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
