#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform plan"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: terraform_plan

short_description: Module to manage Terraform speculative execution plans, and show what actions Terraform would take to apply the current configuration.

version_added: "1.2.0"

description: Generates a speculative execution plan showing what actions Terraform would take to apply the current configuration. This module will not actually perform the planned actions.

options:
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    destroy:
        description: Select the destroy planning mode which creates a plan to destroy all objects currently managed by this Terraform configuration instead of the usual behavior.
        required: false
        default: false
        type: bool
    generate_config:
        description: If import blocks are present in configuration, then instructs Terraform to generate HCL for any imported resources not already present. The configuration is written to a new file at the parameter value which must not already exist. Terraform may still attempt to write configuration if the plan errors.
        required: false
        type: path
    out:
        description: Write a plan file to the given parameter value. This can be used as input to the apply module.
        required: false
        type: path
    refresh_only:
        description: Select the refresh only planning mode which checks whether remote objects still match the outcome of the most recent Terraform apply, but does not propose any actions to undo any changes made outside of Terraform.
        required: false
        default: false
        type: bool
    replace:
        description: Force replacement of a particular resource instance using its resource address. If the plan would normally produce an update or no-op action for this instance, then Terraform will plan to replace it instead.
        required: false
        type: list
    target:
        description: Limit the planning operation to only the given module, resource, or resource instance, and all of its dependencies.
        required: false
        type: list
    var:
        description: Set values for one or more of the input variables in the root module of the configuration.
        required: false
        type: dict
    var_file:
        description: Load variable values from the given HCL2 files in addition to the default files terraform.tfvars and *.auto.tfvars.
        required: false
        type: list


requirements:
    - terraform >= 1.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# produce destroy plan for /path/to/terraform_config_dir
- name: Produce destroy plan for /path/to/terraform_config_dir
  mschuchard.general.terraform_plan:
    config_dir: /path/to/terraform_config_dir
    destroy: true

# produce plan that replaces two resources, and output the result to plan.tfplan
- name: Produce plan that replaces two resources, and output the result to plan.tfplan
  mschuchard.general.terraform_plan:
    replace:
    - aws_instance.this
    - local_file.that
    out: plan.tfplan

# produce plan to check configuration drift with variable inputs
- name: Produce plan to check configuration drift with variable inputs
  mschuchard.general.terraform_plan:
    refresh_only: true
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
    sample: 'terraform plan -out plan.tfplan'
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import terraform


def main() -> None:
    """primary function for terraform plan module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'destroy': {'type': 'bool', 'required': False},
            'generate_config': {'path': 'path', 'required': False},
            'out': {'type': 'path', 'required': False},
            'refresh_only': {'type': 'bool', 'required': False},
            'replace': {'type': 'list', 'required': False},
            'target': {'type': 'list', 'required': False},
            'var': {'type': 'dict', 'required': False},
            'var_file': {'type': 'list', 'required': False},
        },
        supports_check_mode=True,
    )

    # initialize
    config_dir: Path = Path(module.params.get('config_dir'))
    generate_config: Path = module.params.get('generate_config')
    out: Path = module.params.get('out')
    replace: list[str] = module.params.get('replace')
    target: list[str] = module.params.get('target')
    var: dict = module.params.get('var')
    var_file: list[Path] = module.params.get('var_file')

    # check flags
    flags: set[str] = set()
    if module.params.get('destroy'):
        flags.add('destroy')
    if module.params.get('refresh_only'):
        flags.add('refresh_only')

    # check args
    args: dict = {}
    # ruff complains so default should protect against falsey with None
    if generate_config:
        args.update({'generate_config': Path(generate_config)})
    if out:
        args.update({'out': Path(out)})
    if replace:
        args.update({'replace': replace})
    if target:
        args.update({'target': target})
    if var:
        args.update({'var': var})
    if var_file:
        args.update({'var_file': var_file})

    # convert ansible params to terraform args
    args = terraform.ansible_to_terraform(args)

    # determine terraform command
    command: list[str] = terraform.cmd(action='plan', flags=flags, args=args, target_dir=config_dir)

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
