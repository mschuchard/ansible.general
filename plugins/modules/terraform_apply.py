#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform apply"""
__metaclass__ = type

DOCUMENTATION = r'''
---
module: terraform_apply

short_description: Module to manage Terraform configuration applications, and update infrastructure accordingly.

version_added: "1.2.0"

description: Creates or updates infrastructure according to Terraform configuration files in the root module directory.

options:
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    destroy:
        description: Destroy Terraform-managed infrastructure.
        required: false
        type: bool
    plan_file:
        description: Location of the output file generated during a plan. Mutually exclusive with all other parameters since the parameters are all defined instead during the plan execution.
        required: false
        type: path
    replace:
        description: Force replacement of a particular resource instance using its resource address. If the plan would normally produce an update or no-op action for this instance, then Terraform will plan to replace it instead.
        required: false
        type: list
    target:
        description: Limit the applying operation to only the given module, resource, or resource instance, and all of its dependencies.
        required: false
        type: list
    var:
        description: Set values for one or more of the input variables in the root module of the configuration.
        required: false
        type: list
    var_file:
        description: Load variable values from the given HCL2 files in addition to the default files terraform.tfvars and *.auto.tfvars.
        required: false
        type: list


requirements:
    - terraform >= 1.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# destroy infrastructure defined within /path/to/terraform_config_dir
- name: Destroy infrastructure defined within /path/to/terraform_config_dir
  mschuchard.general.terraform_apply:
    config_dir: /path/to/terraform_config_dir
    destroy: true

# apply planned infrastructure changes defined within the plan.tfplan file
- name: Apply planned infrastructure changes defined within the plan.tfplan file
  mschuchard.general.terraform_apply:
      plan_file: plan.tfplan

# apply infrastructures changes to two specific resources with variable inputs
- name: Apply infrastructures changes to two specific resources with variable inputs
  mschuchard.general.terraform_apply:
    target:
    - aws_instance.this
    - local_file.that
    var:
    - var_name: var_value
    - var_name_other: var_value_other
    var_file:
    - one.tfvars
    - two.tfvars
'''

RETURN = r'''
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform apply plan.tfplan'
'''

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import terraform


def main() -> None:
    """primary function for terraform apply module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'destroy': {'type': 'bool', 'required': False},
            'plan_file': {'type': 'path', 'required': False},
            'replace': {'type': 'list', 'required': False},
            'target': {'type': 'list', 'required': False},
            'var': {'type': 'list', 'required': False},
            'var_file': {'type': 'list', 'required': False}
        },
        mutually_exclusive=[('plan_file', 'config_dir')],
        supports_check_mode=True
    )

    # initialize
    changed: bool = True
    config_dir: Path = Path(module.params.get('config_dir'))
    replace: list[str] = module.params.get('replace')
    target: list[str] = module.params.get('target')
    var: list[dict] = module.params.get('var')
    var_file: list[Path] = module.params.get('var_file')

    command: list[str] = []

    # check plan arg first since all others ignored if specified
    if module.params.get('plan_file'):
        # define a command that applies the plan file
        command = terraform.cmd(action='apply', target_dir=module.params.get('plan_file'))
    # else check flags and other args
    else:
        # check flags
        flags: list[str] = []
        if module.params.get('destroy'):
            flags.append('destroy')

        # check args
        args: dict = {}
        # ruff complains so default should protect against falsey with None
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
        command: list[str] = terraform.cmd(action='apply', flags=flags, args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute terraform
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir, environ_update={'TF_IN_AUTOMATION':'true'})

    # check idempotence
    if '0 added, 0 changed, 0 destroyed' in stdout:
        changed = False

    # post-process
    if return_code == 0:
        module.exit_json(changed=changed, stdout=stdout, stderr=stderr, command=command)
    else:
        module.fail_json(
            msg=stderr.rstrip(), return_code=return_code, cmd=command,
            stdout=stdout, stdout_lines=stdout.splitlines(),
            stderr=stderr, stderr_lines=stderr.splitlines())


if __name__ == '__main__':
    main()
