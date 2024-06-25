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
        type: str
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
    sample: 'terraform init -machine-readable /home/terraform'
'''

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import terraform


def main() -> None:
    """primary function for terraform init module"""



if __name__ == '__main__':
    main()
