#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform init"""
__metaclass__ = type

DOCUMENTATION = r'''
---
module: terraform_init

short_description: Module to manage Terraform root module directory initialization.

version_added: "1.1.0"

description: Initialize a new or existing Terraform working directory by creating initial files, loading any remote state, downloading modules, etc. This is the first command that should be run for any new or existing Terraform configuration per machine. This sets up all the local data necessary to run Terraform that is typically not committed to version control. This command is always safe to run multiple times. Though subsequent runs may give errors, this command will never delete your configuration or state. Even so, if you have important information, please back it up prior to running this command, just in case.

options:
    backend:
        description: Disable backend or Terraform Cloud initialization for this configuration, and use what was previously initialized instead.
        required: false
        default: true
        type: bool
    backend_config:
        description: Configurations to be merged with what is in the configuration file's 'backend' block. These can be either paths to HCL files with key/value assignments (same format as terraform.tfvars), or key-value pairs. Files should be a string type element in the list, and key-value pairs should be a single-level dictionary type element in the list. The backend type must be in the configuration itself.
        required: false
        default: []
        type: list
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    force_copy:
        description: Suppress prompts about copying state data when initializating a new state backend. This is equivalent to providing a "yes" to all confirmation prompts.
        required: false
        default: false
        type: bool
    migrate_state:
        description: Reconfigure a backend, and attempt to migrate any existing state.
        required: false
        default: false
        type: bool
    plugin_dir:
        description: Directories containing plugin binaries. These override all default search paths for plugins, and prevents the automatic installation of plugins.
        required: false
        default: []
        type: list
    upgrade:
        description: Install the latest module and provider versions allowed within configured constraints. This overrides the default behavior of selecting exactly the versions recorded in the dependency lockfile.
        required: false
        default: false
        type: bool


requirements:
    - terraform >= 1.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# initialize directory in /path/to/terraform_config_dir
- name: Initialize terraform directory in /path/to/terraform_config_dir
  mschuchard.general.terraform_init:
    config_dir: /path/to/terraform_config_dir

# initialize current directory, upgrade plugins, and disable backend
- name: Initialize current terraform directory, upgrade plugins, and disable backend
  mschuchard.general.terraform_init:
    upgrade: true
    backend: false

# initialize directory in /path/to/terraform_config_dir, migrate the state, utilize two plugin directories, and assign backend_config with both a file and a key-value pair
- name: Initialize directory in /path/to/terraform_config_dir, migrate the state, utilize two plugin directories, and assign backend_config with both a file and a key-value pair
  mschuchard.general.terraform_init:
    config_dir: /path/to/terraform_config_dir
    migrate_state: true
    backend_config:
    - /path/to/backend_config.hcl
    - scheme: https
    plugin_dir:
    - /path/to/plugin_dir
    - /path/to/other_plugin_dir
'''

RETURN = r'''
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform init /home/terraform'
'''

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import terraform


def main() -> None:
    """primary function for terraform init module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'backend': {'type': 'bool', 'required': False, 'default': True},
            'backend_config': {'type': 'list', 'required': False},
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'force_copy': {'type': 'bool', 'required': False},
            'migrate_state': {'type': 'bool', 'required': False},
            'plugin_dir': {'type': 'list', 'required': False},
            'upgrade': {'type': 'bool', 'required': False}
        },
        supports_check_mode=True
    )

    # initialize
    changed: bool = False
    backend_config: list[(str, dict[str, str])] = module.params.get('backend_config')
    config_dir: Path = Path(module.params.get('config_dir'))
    plugin_dir: list[str] = module.params.get('plugin_dir')

    # check flags
    flags: list[str] = []
    if module.params.get('force_copy'):
        flags.append('force_copy')
    if module.params.get('migrate_state'):
        flags.append('migrate_state')
    if module.params.get('upgrade'):
        flags.append('upgrade')

    # check args
    args: dict = {}
    # reminder: the flag that must be argued instead
    # ruff complains so default should protect against falsey with None
    if not module.params.get('backend'):
        args.update({'backend': 'false'})
    if backend_config:
        args.update({'backend_config': backend_config})
    if plugin_dir:
        args.update({'plugin_dir': plugin_dir})

    # convert ansible params to terraform args
    args = terraform.ansible_to_terraform(args)

    # determine terraform command
    command: list[str] = terraform.cmd(action='init', flags=flags, args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute terraform
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir)

    # check idempotence
    if 'successfully initialized' in stdout:
        changed = True

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
