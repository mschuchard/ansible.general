#!/usr/bin/python

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform init"""

DOCUMENTATION = r"""
---
module: terraform_init

short_description: Module to manage Terraform root module directory initialization.

version_added: "1.1.0"

description: Initialize a new or existing Terraform working directory by creating initial files, loading any remote state, downloading modules, etc. This is the first command that should be run for any new or existing Terraform configuration per machine. This sets up all the local data necessary to run Terraform that is typically not committed to version control. This command is always safe to run multiple times. Though subsequent runs may give errors, this command will never delete your configuration or state. Even so, if you have important information, please back it up prior to running this command, just in case.

options:
    backend:
        description: Disable backend or HCP Terraform initialization for this configuration, and use what was previously initialized instead.
        required: false
        default: true
        type: bool
    backend_config:
        description: Configurations to be merged with what is in the configuration file's 'backend' block. These can be either paths to HCL files with key/value assignments (same format as terraform.tfvars), or key-value pairs. Files should be a string type element in the list, and key-value pairs should be a single-level dictionary type element in the list. The backend type must be in the configuration itself.
        required: false
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
    from_module:
        description: Copy the contents of the given module into the target directory before initialization.
        required: false
        type: str
        new_in_version: "1.4.4"
    get:
        description: Download modules for this configuration. Set to false to disable downloading modules.
        required: false
        default: true
        type: bool
        new_in_version: "1.4.4"
    ignore_remote_version:
        description: A rare option used for HCP Terraform and the remote backend only. Ignore checking that the local and remote Terraform versions use compatible state representations, making an operation proceed even when there is a potential mismatch.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.4"
    json:
        description: Machine readable output will be output to stdout in JSON format.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.4"
    lock:
        description: Hold a state lock during backend migration. Disabling this is dangerous if others might concurrently run commands against the same workspace.
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
    lockfile:
        description: Set a dependency lockfile mode. Currently only 'readonly' is valid.
        required: false
        type: str
        choices: ['readonly']
        new_in_version: "1.4.4"
    migrate_state:
        description: Reconfigure a backend, and attempt to migrate any existing state.
        required: false
        default: false
        type: bool
    plugin_dir:
        description: Directories containing plugin binaries. These override all default search paths for plugins, and prevents the automatic installation of plugins.
        required: false
        type: list
        elements: path
    reconfigure:
        description: Reconfigure a backend, ignoring any saved configuration.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.4"
    test_dir:
        description: Set the Terraform test directory.
        required: false
        default: tests
        type: path
        new_in_version: "1.4.4"
    upgrade:
        description: Install the latest module and provider versions allowed within configured constraints. This overrides the default behavior of selecting exactly the versions recorded in the dependency lockfile.
        required: false
        default: false
        type: bool


requirements:
    - terraform >= 1.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
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

# initialize current directory from a module source without downloading modules, using a readonly dependency lockfile and json output
- name: Initialize current directory from a module source without downloading modules, using a readonly dependency lockfile and json output
  mschuchard.general.terraform_init:
    from_module: /path/to/source_module
    get: false
    lockfile: readonly
    json: true

# initialize current directory while reconfiguring the backend, retrying the state lock for up to one minute, and using a custom test directory
- name: Initialize current directory while reconfiguring the backend, retrying the state lock for up to one minute, and using a custom test directory
  mschuchard.general.terraform_init:
    reconfigure: true
    lock_timeout: 1m
    test_dir: my_tests

# initialize current directory without holding a state lock and while ignoring the remote backend version
- name: Initialize current directory without holding a state lock and while ignoring the remote backend version
  mschuchard.general.terraform_init:
    lock: false
    ignore_remote_version: true
"""

RETURN = r"""
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform init /home/terraform'
"""

from pathlib import Path

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mschuchard.general.plugins.module_utils import terraform, universal


def main() -> None:
    """primary function for terraform init module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'backend': {'type': 'bool', 'required': False, 'default': True},
            'backend_config': {'type': 'list', 'required': False},
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'force_copy': {'type': 'bool', 'required': False},
            'from_module': {'type': 'str', 'required': False, 'new_in_version': '1.4.4'},
            'get': {'type': 'bool', 'required': False, 'default': True, 'new_in_version': '1.4.4'},
            'ignore_remote_version': {'type': 'bool', 'required': False, 'new_in_version': '1.4.4'},
            'json': {'type': 'bool', 'required': False, 'new_in_version': '1.4.4'},
            'lock': {'type': 'bool', 'required': False, 'default': True, 'new_in_version': '1.4.4'},
            'lock_timeout': {'type': 'str', 'required': False, 'new_in_version': '1.4.4'},
            'lockfile': {'type': 'str', 'required': False, 'choices': ['readonly'], 'new_in_version': '1.4.4'},
            'migrate_state': {'type': 'bool', 'required': False},
            'plugin_dir': {'type': 'list', 'elements': 'path', 'required': False},
            'reconfigure': {'type': 'bool', 'required': False, 'new_in_version': '1.4.4'},
            'test_dir': {'type': 'path', 'required': False, 'new_in_version': '1.4.4'},
            'upgrade': {'type': 'bool', 'required': False},
        },
        supports_check_mode=True,
    )

    # initialize
    changed: bool = False
    backend_config: list[Path | dict[str, str]] = module.params.get('backend_config')
    config_dir: Path = Path(module.params.pop('config_dir'))
    from_module: str | None = module.params.get('from_module')
    lock_timeout: str | None = module.params.get('lock_timeout')
    lockfile: str | None = module.params.get('lockfile')
    plugin_dir: list[Path] = module.params.get('plugin_dir')
    test_dir: Path | None = module.params.get('test_dir')
    # these bools default to true and are the inverse of their terraform flags, so pop them to prevent the flags converter from treating the default as a flag
    backend: bool = module.params.pop('backend')
    get_modules: bool = module.params.pop('get')
    lock_state: bool = module.params.pop('lock')

    # check flags
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # check args
    args: dict = {}
    # reminder: the flag that must be argued instead
    # ruff complains so default should protect against falsey with None
    if backend is False:
        args.update({'backend': 'false'})
    if backend_config:
        args.update({'backend_config': backend_config})
    if from_module:
        args.update({'from_module': from_module})
    if get_modules is False:
        args.update({'get': 'false'})
    if lock_state is False:
        args.update({'lock': 'false'})
    if lock_timeout:
        args.update({'lock_timeout': lock_timeout})
    if lockfile:
        args.update({'lockfile': lockfile})
    if plugin_dir:
        args.update({'plugin_dir': plugin_dir})
    if test_dir:
        args.update({'test_dir': str(Path(test_dir))})

    # convert ansible params to terraform args
    terraform.ansible_to_terraform(args)

    # determine terraform command
    command: list[str] = terraform.cmd(action='init', flags=flags_args[0], args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute terraform
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir, environ_update={'TF_IN_AUTOMATION': 'true'})

    # check idempotence
    if 'successfully initialized' in stdout:
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
