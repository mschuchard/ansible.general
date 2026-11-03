#!/usr/bin/python

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform validate"""

DOCUMENTATION = r"""
---
module: terraform_validate

short_description: Module to validate Terraform module configuration directories and files.

version_added: "1.1.0"

description: Validates the configuration files in a directory; referring only to the configuration and not accessing any remote services such as remote state, provider APIs, etc. Validate runs checks that verify whether a configuration is syntactically valid and internally consistent. This is regardless of any provided variables or existing state. It is thus primarily useful for general verification of reusable modules. This includes correctness of attribute names and value types. Validation requires an initialized working directory with any referenced plugins and modules installed. To initialize a working directory for validation without accessing any configured remote backend, use the init module with the backend parameter set to false.

options:
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    json:
        description: Machine readable output will be output to stdout in JSON format. This always disables color.
        required: false
        default: false
        type: bool
    query:
        description: Also validate .tfquery.hcl files.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.4"
    test_dir:
        description: Set the Terraform test directory.
        required: false
        default: tests
        type: path
    tests:
        description: Validate test files. Set to false to prevent Terraform from validating test files.
        required: false
        default: true
        type: bool
        new_in_version: "1.4.4"


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

# execute validation for current directory without validating test files
- name: Execute validation for current directory without validating test files
  mschuchard.general.terraform_validate:
    tests: false

# execute validation for current directory including query files
- name: Execute validation for current directory including query files
  mschuchard.general.terraform_validate:
    query: true
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
from ansible_collections.mschuchard.general.plugins.module_utils import terraform, universal


def main() -> None:
    """primary function for terraform validate module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'json': {'type': 'bool', 'required': False},
            'query': {'type': 'bool', 'required': False, 'new_in_version': '1.4.4'},
            'test_dir': {'type': 'path', 'required': False},
            'tests': {'type': 'bool', 'required': False, 'default': True, 'new_in_version': '1.4.4'},
        },
        supports_check_mode=True,
    )

    # initialize
    config_dir: Path = Path(module.params.pop('config_dir'))
    # this bool defaults to true and is the inverse of its terraform flag, so pop it to prevent the flags converter from treating the default as a flag
    tests: bool = module.params.pop('tests')

    # check optional params
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # reminder: the flag that must be argued instead
    if tests is False:
        flags_args[0].add('no_tests')

    # convert ansible params to terraform args
    terraform.ansible_to_terraform(flags_args[1])

    # determine terraform command
    command: list[str] = terraform.cmd(action='validate', flags=flags_args[0], args=flags_args[1], target_dir=config_dir)

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
