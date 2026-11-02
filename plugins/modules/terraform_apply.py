#!/usr/bin/python

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform apply"""

DOCUMENTATION = r"""
---
module: terraform_apply

short_description: Module to manage Terraform configuration applications, and update infrastructure accordingly.

version_added: "1.2.0"

description: Creates or updates infrastructure according to Terraform configuration files in the root module directory.

options:
    backup:
        description: Path to backup the existing state file before modifying. Defaults to the state_out path with a ".backup" extension. Set to "-" to disable backup. This is a legacy option for the local backend only.
        required: false
        type: path
        new_in_version: "1.4.4"
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
        description: Destroy Terraform-managed infrastructure.
        required: false
        default: false
        type: bool
    lock:
        description: Hold a state lock during the operation. Disabling this is dangerous if others might concurrently run commands against the same workspace.
        required: false
        default: true
        type: bool
        new_in_version: "1.4.4"
    lock_timeout:
        description: Duration to retry a state lock (duration string, e.g. '0s', '30s', '5m').
        required: false
        default: 0s
        type: str
        new_in_version: "1.4.4"
    parallelism:
        description: Limit the number of parallel resource operations.
        required: false
        default: 10
        type: int
        new_in_version: "1.4.4"
    plan_file:
        description: Location of the output file generated during a plan. Mutually exclusive with all other parameters since the parameters are all defined instead during the plan execution.
        required: false
        type: path
    replace:
        description: Force replacement of a particular resource instance using its resource address. If the plan would normally produce an update or no-op action for this instance, then Terraform will plan to replace it instead.
        required: false
        type: list
        elements: str
    state:
        description: Path to read and save state (unless state_out is specified). Defaults to "terraform.tfstate". This is a legacy option for the local backend only.
        required: false
        type: path
        new_in_version: "1.4.4"
    state_out:
        description: Path to write state to that is different than state. This can be used to preserve the old state. This is a legacy option for the local backend only.
        required: false
        type: path
        new_in_version: "1.4.4"
    target:
        description: Limit the applying operation to only the given module, resource, or resource instance, and all of its dependencies.
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
      var_name: var_value
      var_name_other: var_value_other
    var_file:
    - one.tfvars
    - two.tfvars

# apply infrastructure changes with compact warnings, a state lock retry of thirty seconds, and a parallelism limit of four
- name: Apply infrastructure changes with compact warnings, a state lock retry of thirty seconds, and a parallelism limit of four
  mschuchard.general.terraform_apply:
    compact_warnings: true
    lock_timeout: 30s
    parallelism: 4

# apply infrastructure changes with custom legacy local backend state paths, and without a state backup
- name: Apply infrastructure changes with custom legacy local backend state paths, and without a state backup
  mschuchard.general.terraform_apply:
    state: /path/to/in.tfstate
    state_out: /path/to/out.tfstate
    backup: '-'
"""

RETURN = r"""
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform apply plan.tfplan'
"""

from pathlib import Path

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mschuchard.general.plugins.module_utils import terraform


def main() -> None:
    """primary function for terraform apply module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'backup': {'type': 'path', 'required': False, 'new_in_version': '1.4.4'},
            'compact_warnings': {'type': 'bool', 'required': False, 'new_in_version': '1.4.4'},
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'destroy': {'type': 'bool', 'required': False},
            'lock': {'type': 'bool', 'required': False, 'default': True, 'new_in_version': '1.4.4'},
            'lock_timeout': {'type': 'str', 'required': False, 'new_in_version': '1.4.4'},
            'parallelism': {'type': 'int', 'required': False, 'new_in_version': '1.4.4'},
            'plan_file': {'type': 'path', 'required': False},
            'replace': {'type': 'list', 'elements': 'str', 'required': False},
            'state': {'type': 'path', 'required': False, 'new_in_version': '1.4.4'},
            'state_out': {'type': 'path', 'required': False, 'new_in_version': '1.4.4'},
            'target': {'type': 'list', 'elements': 'str', 'required': False},
            'var': {'type': 'dict', 'required': False},
            'var_file': {'type': 'list', 'elements': 'path', 'required': False},
        },
        mutually_exclusive=[
            ('plan_file', 'config_dir'),
            ('plan_file', 'backup'),
            ('plan_file', 'compact_warnings'),
            ('plan_file', 'lock_timeout'),
            ('plan_file', 'parallelism'),
            ('plan_file', 'state'),
            ('plan_file', 'state_out'),
        ],
        supports_check_mode=True,
    )

    # initialize
    changed: bool = True
    config_dir: Path = Path(module.params.get('config_dir'))
    backup: str = module.params.get('backup')
    lock_timeout: str = module.params.get('lock_timeout')
    parallelism: int = module.params.get('parallelism')
    replace: list[str] = module.params.get('replace')
    state: str = module.params.get('state')
    state_out: str = module.params.get('state_out')
    target: list[str] = module.params.get('target')
    var: dict = module.params.get('var')
    var_file: list[Path] = module.params.get('var_file')

    # check plan arg first since all others ignored if specified
    if module.params.get('plan_file'):
        # define a command that applies the plan file
        command = terraform.cmd(action='apply', target_dir=module.params.get('plan_file'))
    # else check flags and other args
    else:
        # check flags
        flags: set[str] = set()
        if module.params.get('compact_warnings'):
            flags.add('compact_warnings')
        if module.params.get('destroy'):
            flags.add('destroy')
        # reminder: the flag that must be argued instead
        if module.params.get('lock') is False:
            flags.add('lock')

        # check args
        args: dict = {}
        # ruff complains so default should protect against falsey with None
        if backup:
            args.update({'backup': backup})
        if lock_timeout:
            args.update({'lock_timeout': lock_timeout})
        if parallelism:
            args.update({'parallelism': parallelism})
        if replace:
            args.update({'replace': replace})
        if state:
            args.update({'state': state})
        if state_out:
            args.update({'state_out': state_out})
        if target:
            args.update({'target': target})
        if var:
            args.update({'var': var})
        if var_file:
            args.update({'var_file': var_file})

        # convert ansible params to terraform args
        terraform.ansible_to_terraform(args)

        # determine terraform command
        command: list[str] = terraform.cmd(action='apply', flags=flags, args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute terraform
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir, environ_update={'TF_IN_AUTOMATION': 'true'})

    # check idempotence
    if '0 added, 0 changed, 0 destroyed' in stdout:
        changed = False

    # post-process
    if return_code == 0:
        module.exit_json(changed=changed, stdout=stdout, stderr=stderr, command=command)
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
