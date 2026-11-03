#!/usr/bin/python

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform plan"""

DOCUMENTATION = r"""
---
module: terraform_plan

short_description: Module to manage Terraform speculative execution plans, and show what actions Terraform would take to apply the current configuration.

version_added: "1.2.0"

description: Generates a speculative execution plan showing what actions Terraform would take to apply the current configuration. This module will not actually perform the planned actions.

options:
    compact_warnings:
        description: If Terraform produces any warnings that are not accompanied by errors, then show them in a more compact form that includes only the summary messages.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.4"
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
    detailed_exitcode:
        description: Return detailed exit codes when the command exits. An exit code of 0 means the plan succeeded with no changes, 1 means the plan errored, and 2 means the plan succeeded with a diff. The module treats an exit code of 2 as success, and reports the exit code in the return_code return value.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.4"
    generate_config:
        description: If import blocks are present in configuration, then instructs Terraform to generate HCL for any imported resources not already present. The configuration is written to a new file at the parameter value which must not already exist. Terraform may still attempt to write configuration if the plan errors.
        required: false
        type: path
    lock:
        description: Hold a state lock during the operation. Disabling this is dangerous if others might concurrently run commands against the same workspace.
        required: false
        default: true
        type: bool
        new_in_version: "1.4.4"
    lock_timeout:
        description: Duration to retry a state lock (duration string, e.g. '30s', '5m').
        required: false
        default: 0s
        type: str
        new_in_version: "1.4.4"
    out:
        description: Write a plan file to the given parameter value. This can be used as input to the apply module.
        required: false
        type: path
    parallelism:
        description: Limit the number of concurrent operations.
        required: false
        default: 10
        type: int
        new_in_version: "1.4.4"
    refresh:
        description: Check for external changes to remote objects while creating the plan. Setting this to false can potentially make planning faster, but at the expense of possibly planning against a stale record of the remote system state.
        required: false
        default: true
        type: bool
        new_in_version: "1.4.4"
    refresh_only:
        description: Select the refresh only planning mode which checks whether remote objects still match the outcome of the most recent Terraform apply, but does not propose any actions to undo any changes made outside of Terraform.
        required: false
        default: false
        type: bool
    replace:
        description: Force replacement of a particular resource instance using its resource address. If the plan would normally produce an update or no-op action for this instance, then Terraform will plan to replace it instead.
        required: false
        type: list
        elements: str
    target:
        description: Limit the planning operation to only the given module, resource, or resource instance, and all of its dependencies.
        required: false
        type: list
        elements: str
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

# produce plan with detailed exit codes, compact warnings, and no refresh of remote objects
- name: Produce plan with detailed exit codes, compact warnings, and no refresh of remote objects
  mschuchard.general.terraform_plan:
    detailed_exitcode: true
    compact_warnings: true
    refresh: false
  register: plan_result
  failed_when: plan_result.return_code not in [0, 2]

# produce plan while retrying the state lock for up to one minute and limiting concurrent operations to four
- name: Produce plan while retrying the state lock for up to one minute and limiting concurrent operations to four
  mschuchard.general.terraform_plan:
    lock_timeout: 1m
    parallelism: 4

# produce plan without holding a state lock
- name: Produce plan without holding a state lock
  mschuchard.general.terraform_plan:
    lock: false
"""

RETURN = r"""
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform plan -out plan.tfplan'
return_code:
    description: The return code from the Terraform plan execution. With detailed_exitcode enabled, a value of 2 indicates the plan succeeded with a diff.
    type: int
    returned: when the command is executed
"""

from pathlib import Path

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mschuchard.general.plugins.module_utils import terraform, universal


def main() -> None:
    """primary function for terraform plan module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'compact_warnings': {'type': 'bool', 'required': False, 'new_in_version': '1.4.4'},
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'destroy': {'type': 'bool', 'required': False},
            'detailed_exitcode': {'type': 'bool', 'required': False, 'new_in_version': '1.4.4'},
            'generate_config': {'type': 'path', 'required': False},
            'lock': {'type': 'bool', 'required': False, 'default': True, 'new_in_version': '1.4.4'},
            'lock_timeout': {'type': 'str', 'required': False, 'new_in_version': '1.4.4'},
            'out': {'type': 'path', 'required': False},
            'parallelism': {'type': 'int', 'required': False, 'new_in_version': '1.4.4'},
            'refresh': {'type': 'bool', 'required': False, 'default': True, 'new_in_version': '1.4.4'},
            'refresh_only': {'type': 'bool', 'required': False},
            'replace': {'type': 'list', 'elements': 'str', 'required': False},
            'target': {'type': 'list', 'elements': 'str', 'required': False},
            'var': {'type': 'dict', 'required': False},
            'var_file': {'type': 'list', 'elements': 'path', 'required': False},
        },
        supports_check_mode=True,
    )

    # initialize
    config_dir: Path = Path(module.params.pop('config_dir'))
    # these bools default to true and are the inverse of their terraform flags, so pop them to prevent the flags converter from treating the default as a flag
    lock_state: bool = module.params.pop('lock')
    refresh: bool = module.params.pop('refresh')
    # terraform.cmd only accepts str values for args, so pop the int to convert it manually
    parallelism: int | None = module.params.pop('parallelism')

    # check optional params
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # reminder: the flag that must be argued instead
    if lock_state is False:
        flags_args[1].update({'lock': 'false'})
    if refresh is False:
        flags_args[1].update({'refresh': 'false'})
    # zero is not a valid value for terraform, so only protect against None
    if parallelism is not None:
        flags_args[1].update({'parallelism': str(parallelism)})

    # convert ansible params to terraform args
    terraform.ansible_to_terraform(flags_args[1])

    # determine terraform command
    command: list[str] = terraform.cmd(action='plan', flags=flags_args[0], args=flags_args[1], target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute terraform
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir, environ_update={'TF_IN_AUTOMATION': 'true'})

    # with detailed exit codes enabled, a return code of 2 indicates success with a diff and is not an error
    detailed_exitcode_diff: bool = 'detailed_exitcode' in flags_args[0] and return_code == 2

    # post-process
    if return_code == 0 or detailed_exitcode_diff:
        module.exit_json(changed=False, stdout=stdout, stderr=stderr, return_code=return_code, command=command)
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
