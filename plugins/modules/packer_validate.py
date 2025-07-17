#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for packer validate"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: packer_validate

short_description: Module to manage Packer template and config validation.

version_added: "1.0.0"

description: Checks the template is valid by parsing the template and also checking the configuration with the various builders, provisioners, etc. If it is not valid, the errors will be shown and the module task will exit as a failure.

options:
    config_dir:
        description: Location of the directory or file containing the Packer template(s) and/or config(s).
        required: false
        default: cwd
        type: str
    evaluate_datasources:
        description: Evaluate data sources during validation (>= 1.8.5)
        required: false
        default: false
        type: bool
    excepts:
        description: Validate all builds other than these.
        required: false
        type: list
    only:
        description: Validate only these builds.
        required: false
        type: list
    syntax_only:
        description: Only check syntax. Do not verify config of the template.
        required: false
        default: false
        type: bool
    var:
        description: Variables for templates.
        required: false
        type: dict
    var_file:
        description: HCL2 files containing user variables.
        required: false
        type: list
    warn_undeclared_var:
        description: Warnings for user variable files containing undeclared variables (>= 1.8.5)
        required: false
        default: true
        type: bool

requirements:
    - packer >= 1.7.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# validate packer templates and configs in /path/to/packer_dir
- name: Validate packer templates and configs in /path/to/packer_dir
  mschuchard.general.packer_validate:
    config_dir: /path/to/packer_dir

# validate packer files without warning on undeclared variables, and while evaluating datasources
- name: Validate packer files without warning on undeclared variables, and while evaluating datasources
  mschuchard.general.packer_validate:
    config_dir: /path/to/packer_dir
    evaluate_datasources: true
    warn_undeclared_var: false

# validate only the syntax of the null.this and null.that builds in the packer files
- name: Validate only the null.this and null.that builds in the packer files
  mschuchard.general.packer_validate:
    config_dir: /path/to/packer_dir
    only:
    - null.this
    - null.that
    syntax_only: true

# validate the packer files with vars and var files
- name: Validate the packer files with vars and var files
  mschuchard.general.packer_validate:
    config_dir: /path/to/packer_dir
    var:
      var_name: var_value
      var_name_other: var_value_other
    var_file:
    - one.pkrvars.hcl
    - two.pkrvars.hcl
"""

RETURN = r"""
command:
    description: The raw Packer command executed by Ansible.
    type: str
    returned: always
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import packer


def main() -> None:
    """primary function for packer validate module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'evaluate_datasources': {'type': 'bool', 'required': False},
            'excepts': {'type': 'list', 'required': False},
            'only': {'type': 'list', 'required': False},
            'syntax_only': {'type': 'bool', 'required': False},
            'var': {'type': 'dict', 'required': False},
            'var_file': {'type': 'list', 'required': False},
            'warn_undeclared_var': {'type': 'bool', 'required': False, 'default': True},
        },
        mutually_exclusive=[('excepts', 'only')],
        supports_check_mode=True,
    )

    # initialize
    config_dir: Path = Path(module.params.get('config_dir'))
    excepts: list[str] = module.params.get('excepts')
    only: list[str] = module.params.get('only')
    var: dict = module.params.get('var')
    var_file: list[Path] = module.params.get('var_file')

    # check flags
    flags: set[str] = set()
    if module.params.get('evaluate_datasources'):
        flags.add('evaluate_datasources')
    if module.params.get('syntax_only'):
        flags.add('syntax_only')
    if module.params.get('warn_undeclared_var') is False:
        flags.add('no_warn_undeclared_var')

    # check args
    args: dict = {}
    if excepts:
        args.update({'excepts': excepts})
    if only:
        args.update({'only': only})
    if var:
        args.update({'var': var})
    if var_file:
        args.update({'var_file': var_file})

    # convert ansible params to packer args
    args = packer.ansible_to_packer(args)

    # determine packer command
    command: list[str] = packer.cmd(action='validate', flags=flags, args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute packer
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir)

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
