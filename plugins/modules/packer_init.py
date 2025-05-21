#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for packer init"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: packer_init

short_description: Module to manage Packer template and config directory initialization.

version_added: "1.0.0"

description: Install all the missing plugins required in a Packer config. Note that Packer does not have a state. This is the first command that should be executed when working with a new or existing template. This command is always safe to run multiple times. Though subsequent runs may give errors, this command will never delete anything.

options:
    config_dir:
        description: Location of the directory containing the Packer config file.
        required: false
        default: cwd
        type: str
    upgrade:
        description: Update installed plugins to the latest available version if there is a new higher one. Note that this still considers the version constraint of the config.
        required: false
        default: false
        type: bool

requirements:
    - packer >= 1.7.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# initialize directory in /path/to/packer_config_dir
- name: Initialize packer directory in /path/to/packer_config_dir
  mschuchard.general.packer_init:
    config_dir: /path/to/packer_config_dir

# initialize current directory and upgrade plugins
- name: Initialize current packer directory and upgrade plugins
  mschuchard.general.packer_init:
    upgrade: true

# initialize directory in /path/to/packer_config_dir and upgrade plugins
- name: Initialize packer directory in /path/to/packer_config_dir and upgrade plugins
  mschuchard.general.packer_init:
    config_dir: /path/to/packer_config_dir
    upgrade: true
"""

RETURN = r"""
command:
    description: The raw Packer command executed by Ansible.
    type: str
    returned: always
    sample: 'packer init -machine-readable /home/packer'
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import packer


def main() -> None:
    """primary function for packer init module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()}, 'upgrade': {'type': 'bool', 'required': False}},
        supports_check_mode=True,
    )

    # initialize
    changed: bool = False
    config_dir: Path = Path(module.params.get('config_dir'))

    # check on optional upgrade param
    flags: set[str] = set()
    if module.params.get('upgrade'):
        flags.add('upgrade')

    # determine packer command
    command: list[str] = packer.cmd(action='init', flags=flags, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute packer
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir)

    # check idempotence
    if len(stdout) > 0:
        changed = True

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
