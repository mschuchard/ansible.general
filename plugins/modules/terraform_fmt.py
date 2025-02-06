#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform fmt"""
__metaclass__ = type

DOCUMENTATION = r'''
---
module: terraform_fmt

short_description: Module to manage Terraform automatic canonical formatting.

version_added: "1.1.0"

description: Rewrites all Terraform configuration files to a canonical format. All configuration files (.tf), variables files (.tfvars), and testing files (.tftest.hcl) are updated. JSON files (.tf.json, .tfvars.json, or .tftest.json) are not modified.

options:
    check:
        description: Check if the input is formatted. Exit status will be 0 if all input is properly formatted and non-zero otherwise.
        required: false
        default: false
        type: bool
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    diff:
        description: Display diffs of formatting changes.
        required: false
        default: false
        type: bool
    recursive:
        description: Also process files in subdirectories.
        required: false
        default: false
        type: bool
    write:
        description: Write to source files.
        required: false
        default: true
        type: bool


requirements:
    - terraform >= 1.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# format terraform config files in /path/to/terraform_config_dir, display diffs, and do not write to source files
- name: Format terraform config files in /path/to/terraform_config_dir, display diffs, and do not write to source files
  mschuchard.general.terraform_fmt:
    config_dir: /path/to/terraform_config_dir
    diff: true
    write: false

# check format of terraform config files in current directory and subdirectories
- name: Check format of terraform config files in current directory and subdirectories
  mschuchard.general.terraform_fmt:
    check: true
    recursive: true
'''

RETURN = r'''
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform test -json'
'''

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import terraform


def main() -> None:
    """primary function for terraform test module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'check': {'type': 'bool', 'required': False},
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'diff': {'type': 'bool', 'required': False},
            'recursive': {'type': 'bool', 'required': False},
            'write': {'type': 'bool', 'required': False, 'default': True},
        },
        mutually_exclusive=[('check', 'write')],
        supports_check_mode=True
    )

    # initialize
    config_dir: Path = Path(module.params.get('config_dir'))
    changed: bool = True

    # check flags
    flags: list[str] = []
    if module.params.get('check'):
        flags.append('check')
        changed = False
    if module.params.get('diff'):
        flags.append('diff')
    if module.params.get('recursive'):
        flags.append('recursive')

    # check args
    args: dict = {}
    # reminder: the flag that must be argued instead
    # ruff complains so default should protect against falsey with None
    if not module.params.get('write'):
        args.update({'write': 'false'})
        changed = False

    # convert ansible params to terraform args
    args = terraform.ansible_to_terraform(args)

    # determine terraform command
    command: list[str] = terraform.cmd(action='fmt', flags=flags, args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute terraform
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir, environ_update={'TF_IN_AUTOMATION':'true'})

    # check idempotence
    if len(stdout) == 0:
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
