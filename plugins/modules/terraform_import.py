#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform import"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: terraform_import

short_description: Module to manage importing existing infrastructure into the Terraform state.

version_added: "1.1.0"

description: This will find and import the specified resource into your Terraform state, allowing existing infrastructure to come under Terraform management without having to be initially created by Terraform. The address specified is the address to import the resource to. Please see the documentation online for resource addresses. The ID is a resource-specific ID to identify that resource being imported. Please reference the documentation for the resource type you are importing to determine the ID syntax to use. It typically matches directly to the ID that the provider uses. This command will not modify your infrastructure, but it will make network requests to inspect parts of your infrastructure relevant to the resource being imported.

options:
    address:
        description: The Terraform resource namespace for the state address.
        required: true
        type: str
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    id:
        description: The object identifier value.
        required: true
        type: str
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
# import resource using provider configuration in /path/to/terraform_config_dir
- name: Import resource using provider configuration in /path/to/terraform_config_dir
  mschuchard.general.terraform_import:
    config_dir: /path/to/terraform_config_dir
    address: aws_instance.this
    id: i-1234567890

# import resource for config in current directory with variable inputs
- name: Import resource for config in current directory with variable inputs
  mschuchard.general.terraform_import:
    address: local_file.this
    id: /path/to/local_file
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
    sample: 'terraform import aws_instance.this i-1234567890'
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import terraform


def main() -> None:
    """primary function for terraform validate module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'address': {'type': 'str', 'required': True},
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'id': {'type': 'str', 'required': True},
            'var': {'type': 'dict', 'required': False},
            'var_file': {'type': 'list', 'elements': 'path', 'required': False},
        },
        supports_check_mode=True,
    )

    # initialize
    changed: bool = False
    config_dir: Path = Path(module.params.get('config_dir'))
    address: str = module.params.get('address')
    id: str = module.params.get('id')
    var: dict = module.params.get('var')
    var_file: list[Path] = module.params.get('var_file')

    # check args
    args: dict = {}
    if var:
        args.update({'var': var})
    if var_file:
        args.update({'var_file': var_file})
    # needs to be last because it is positional argument to terraform import
    args.update({'resource': {address: id}})

    # convert ansible params to terraform args
    args = terraform.ansible_to_terraform(args)

    # determine terraform command
    command: list[str] = terraform.cmd(action='import', args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=changed, command=command)

    # execute terraform
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir, environ_update={'TF_IN_AUTOMATION': 'true'})

    # check idempotence
    if 'Import successful!' in stdout:
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
